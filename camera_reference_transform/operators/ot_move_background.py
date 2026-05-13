from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import bpy
import gpu
import gpu_extras
import mathutils

from camera_reference_transform import addon_info

if TYPE_CHECKING:
    from bpy.stub_internal.rna_enums import OperatorReturnItems

_shader = gpu.shader.from_builtin('UNIFORM_COLOR')


class CAMERA_OT_move_background(bpy.types.Operator):
    """Move camera background image"""

    bl_idname = "camera.background_move"
    bl_label = "Move Camera Background"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    if TYPE_CHECKING:
        constraint_axis: tuple[bool, bool]
    else:
        constraint_axis: bpy.props.BoolVectorProperty(
            name="Constraint axis",
            description="Axis to constraint background movement",
            subtype='XYZ',
            size=2,
            default=(False, False),
            options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        ob = context.object
        space = context.space_data

        return ob is not None and ob.type == 'CAMERA' and space.region_3d.view_perspective == 'CAMERA'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.cam_ob: bpy.types.Object | None = None
        self.bg: bpy.types.CameraBackgroundImage | None = None

        self.modal_keymap_items = addon_info.get_preferences().modal_keymap_items

        self.last_mouse_x: int = 0
        self.last_mouse_y: int = 0

        self.raw_bg_offset_x: float = 0.0
        self.raw_bg_offset_y: float = 0.0

        self.init_bg_offset_x: float = 0.0
        self.init_bg_offset_y: float = 0.0
        self.init_bg_use_flip_x: bool = False
        self.init_bg_use_flip_y: bool = False

        self.handler: object = None
        self.batch: gpu.types.GPUBatch | None = None

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        self.cam_ob = context.object
        assert self.cam_ob is not None and self.cam_ob.type == 'CAMERA'
        assert isinstance(self.cam_ob.data, bpy.types.Camera)
        assert context.window is not None

        self.bg = next((bg for bg in self.cam_ob.data.background_images if bg.image and bg.show_background_image), None)
        if self.bg is None:
            self.report({'WARNING'}, "No visible backgrounds")
            return {'CANCELLED'}

        self.last_mouse_x = event.mouse_region_x
        self.last_mouse_y = event.mouse_region_y
        self.raw_bg_offset_x, self.raw_bg_offset_y = self.bg.offset

        self.init_bg_offset_x, self.init_bg_offset_y = self.bg.offset
        self.init_bg_use_flip_x = self.bg.use_flip_x
        self.init_bg_use_flip_y = self.bg.use_flip_y

        self.redraw_status(context)
        context.window.cursor_modal_set('HAND')

        self.build_shader_batch()
        self.handler = context.space_data.draw_handler_add(self.draw_constraint, (), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def redraw_status(self, context: bpy.types.Context) -> None:
        """Draw shortcuts in the status."""
        flip_x_key = self.modal_keymap_items["flip_x"].type
        flip_y_key = self.modal_keymap_items["flip_y"].type
        constraint_x_key = self.modal_keymap_items["constraint_x"].type
        constraint_y_key = self.modal_keymap_items["constraint_y"].type

        status_text = (
            f"LMB, ENTER: Confirm | "
            f"RMB, ESC: Cancel | "
            f"{flip_x_key}: Flip Horizontally | "
            f"{flip_y_key}: Flip Vertically | "
            f"{constraint_x_key}: Constraint Horizontal | "
            f"{constraint_y_key}: Constraint Vertical"
        )
        context.workspace.status_text_set(status_text)

    def is_event_match_kmi(self, event: bpy.types.Event, kmi_name: str, release: bool = False) -> bool:
        """Return match between event type and keymap item type."""
        if release:
            return event.type == self.modal_keymap_items[kmi_name].type

        return (
            event.type == (kmi := self.modal_keymap_items[kmi_name]).type
            and event.alt == kmi.alt
            and event.ctrl == kmi.ctrl
            and event.shift == kmi.shift
        )

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        assert self.bg is not None

        if event.type == 'MOUSEMOVE':
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
            mouse_offset_x = mouse_x - self.last_mouse_x
            mouse_offset_y = mouse_y - self.last_mouse_y

            divisor = 6000 if event.shift else 600
            move_offset_x = mouse_offset_x / divisor if not self.constraint_axis[0] else 0
            move_offset_y = mouse_offset_y / divisor if not self.constraint_axis[1] else 0
            self.raw_bg_offset_x += move_offset_x
            self.raw_bg_offset_y += move_offset_y

            if event.ctrl or (
                context.scene.tool_settings.use_snap
                and context.scene.tool_settings.use_snap_scale
                and context.scene.tool_settings.snap_elements == 'INCREMENT'
                and not event.ctrl
            ):
                rounded_x = round(self.raw_bg_offset_x / 0.01) * 0.01
                rounded_y = round(self.raw_bg_offset_y / 0.01) * 0.01
                if self.bg.offset[0] != rounded_x:
                    self.bg.offset[0] = rounded_x
                if self.bg.offset[1] != rounded_y:
                    self.bg.offset[1] = rounded_y
            else:
                self.bg.offset = self.raw_bg_offset_x, self.raw_bg_offset_y

            context.area.header_text_set(f"Background Offset: {self.bg.offset[0]:.4f}, {self.bg.offset[1]:.4f}")

            self.last_mouse_x = event.mouse_region_x
            self.last_mouse_y = event.mouse_region_y

        if event.value == 'PRESS':
            if event.type == 'MIDDLEMOUSE':
                self.constraint_axis = (False, False)

            if self.is_event_match_kmi(event, "constraint_y"):
                if self.constraint_axis == (True, False):
                    self.constraint_axis = (False, False)
                    context.window.cursor_modal_set('HAND')
                else:
                    self.constraint_axis = (True, False)
                    context.window.cursor_modal_set('MOVE_Y')

                self.build_shader_batch()
                context.area.tag_redraw()

            elif self.is_event_match_kmi(event, "constraint_x"):
                if self.constraint_axis == (False, True):
                    self.constraint_axis = (False, False)
                    context.window.cursor_modal_set('HAND')
                else:
                    self.constraint_axis = (False, True)
                    context.window.cursor_modal_set('MOVE_X')

                self.build_shader_batch()
                context.region.tag_redraw()

            elif self.is_event_match_kmi(event, "flip_x"):
                self.bg.use_flip_x = not self.bg.use_flip_x

            elif self.is_event_match_kmi(event, "flip_y"):
                self.bg.use_flip_y = not self.bg.use_flip_y

            elif event.type in ('ESC', 'RIGHTMOUSE'):
                self.undo_changes()
                self.finish_modal(context)
                return {'CANCELLED'}

            elif event.type in ('SPACE', 'LEFTMOUSE'):
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def undo_changes(self):
        assert self.bg is not None
        self.bg.offset = self.init_bg_offset_x, self.init_bg_offset_y
        self.bg.use_flip_x = self.init_bg_use_flip_x
        self.bg.use_flip_y = self.init_bg_use_flip_y

    def finish_modal(self, context: bpy.types.Context):
        context.area.header_text_set(text=None)
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.window.cursor_modal_restore()

    def build_shader_batch(self):
        assert self.cam_ob is not None

        def get_offset_co(mx: mathutils.Matrix, offset: tuple[int, int, int]) -> Sequence[float]:
            offset_mx = mx @ mathutils.Matrix.Translation(offset)
            offset_co = offset_mx.translation[:]
            return offset_co

        draw_offset = (0, 0, -2)
        draw_center_mx = self.cam_ob.matrix_world @ mathutils.Matrix.Translation(draw_offset)

        if self.constraint_axis[0]:
            draw_y_pos = get_offset_co(draw_center_mx, (0, 100, 0))
            draw_y_neg = get_offset_co(draw_center_mx, (0, -100, 0))
            co = [draw_y_neg, draw_y_pos]
        elif self.constraint_axis[1]:
            draw_x_pos = get_offset_co(draw_center_mx, (100, 0, 0))
            draw_x_neg = get_offset_co(draw_center_mx, (-100, 0, 0))
            co = [draw_x_neg, draw_x_pos]
        else:
            return

        self.batch = gpu_extras.batch.batch_for_shader(_shader, 'LINES', {"pos": co})

    def draw_constraint(self):
        assert self.batch is not None

        if self.constraint_axis[0]:
            color = (0, 1, 0, 1)
        elif self.constraint_axis[1]:
            color = (1, 0, 0, 1)
        else:
            return

        _shader.bind()
        _shader.uniform_float("color", color)
        self.batch.draw(_shader)
