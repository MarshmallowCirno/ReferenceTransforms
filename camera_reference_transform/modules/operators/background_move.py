from typing import Optional

import bpy
import gpu
from bpy.types import CameraBackgroundImage
from bpy.types import Object
from gpu.types import GPUBatch
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

from ...package import get_preferences
from ..properties import ModalKeyMapItem
from ..utils.modal import event_match_kmi

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')


class CAMERA_OT_background_move(bpy.types.Operator):
    """Move camera background image"""

    bl_idname = "camera.background_move"
    bl_label = "Move Camera Background"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

    # noinspection PyTypeChecker
    constraint_axis: bpy.props.BoolVectorProperty(
        name="Constraint axis",
        description="Axis to constraint background movement",
        subtype='XYZ',
        size=2,
        default=(False, False),
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        ob = context.object
        space = context.space_data
        return ob and ob.type == 'CAMERA' and space.region_3d.view_perspective == 'CAMERA'

    def __init__(self):
        self.cam: Optional[Object] = None
        self.bg: Optional[CameraBackgroundImage] = None

        self.keymap_items: ModalKeyMapItem = get_preferences().keymaps["modal"].keymap_items

        self.last_mouse_x: int = 0
        self.last_mouse_y: int = 0

        self.bg_offset_x_float: float = 0
        self.bg_offset_y_float: float = 0

        self.init_bg_offset_x: int = 0
        self.init_bg_offset_y: int = 0
        self.init_bg_flip_x: bool = False
        self.init_bg_flip_y: bool = False

        self.handler: object = None
        self.batch: Optional[GPUBatch] = None

    def invoke(self, context, event):
        self.cam = context.object
        cam_backgrounds = [bg for bg in self.cam.data.background_images if bg.image and bg.show_background_image]
        if not any(cam_backgrounds):
            self.report({'WARNING'}, "No visible backgrounds")
            return {'CANCELLED'}

        self.bg = cam_backgrounds[0]
        self.last_mouse_x = event.mouse_region_x
        self.last_mouse_y = event.mouse_region_y

        self.init_bg_offset_x = self.bg_offset_x_float = self.bg.offset[0]
        self.init_bg_offset_y = self.bg_offset_y_float = self.bg.offset[1]
        self.init_bg_flip_x = self.bg.use_flip_x
        self.init_bg_flip_y = self.bg.use_flip_y

        self.redraw_status(context)
        context.window.cursor_modal_set('HAND')

        self.build_shader_batch()
        self.handler = context.space_data.draw_handler_add(self.draw_constraint, (), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def redraw_status(self, context) -> None:
        """Draw shortcuts in the status."""
        flip_x_key = self.keymap_items["flip_x"].type
        flip_y_key = self.keymap_items["flip_y"].type
        constraint_x_key = self.keymap_items["constraint_x"].type
        constraint_y_key = self.keymap_items["constraint_y"].type

        status_text = (
            f"LMB, ENTER: Confirm | "
            f"RMB, ESC: Cancel | "
            f"{flip_x_key}: Flip Horizontally | "
            f"{flip_y_key}: Flip Vertically | "
            f"{constraint_x_key}: Constraint Horizontal | "
            f"{constraint_y_key}: Constraint Vertical"
        )
        context.workspace.status_text_set(status_text)

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
            mouse_offset_x = mouse_x - self.last_mouse_x
            mouse_offset_y = mouse_y - self.last_mouse_y

            divisor = 6000 if event.shift else 600
            move_offset_x = mouse_offset_x / divisor if not self.constraint_axis[0] else 0
            move_offset_y = mouse_offset_y / divisor if not self.constraint_axis[1] else 0
            self.bg_offset_x_float += move_offset_x
            self.bg_offset_y_float += move_offset_y

            if event.ctrl or (context.scene.tool_settings.use_snap
                              and context.scene.tool_settings.use_snap_scale
                              and context.scene.tool_settings.snap_elements == 'INCREMENT'
                              and not event.ctrl):
                rounded_x = round(self.bg_offset_x_float / .01) * .01
                rounded_y = round(self.bg_offset_y_float / .01) * .01
                if self.bg.offset[0] != rounded_x:
                    self.bg.offset[0] = rounded_x
                if self.bg.offset[1] != rounded_y:
                    self.bg.offset[1] = rounded_y
            else:
                self.bg.offset[0] = self.bg_offset_x_float
                self.bg.offset[1] = self.bg_offset_y_float

            context.area.header_text_set(f"Background Offset: {self.bg.offset[0]:.4f}, {self.bg.offset[1]:.4f}")

            self.last_mouse_x = event.mouse_region_x
            self.last_mouse_y = event.mouse_region_y

        if event.value == 'PRESS':
            if event.type == 'MIDDLEMOUSE':
                self.constraint_axis = (False, False)

            if event_match_kmi(self, event, "constraint_y"):
                if self.constraint_axis == (True, False):
                    self.constraint_axis = (False, False)
                    context.window.cursor_modal_set('HAND')
                else:
                    self.constraint_axis = (True, False)
                    context.window.cursor_modal_set('MOVE_Y')

                self.build_shader_batch()
                context.area.tag_redraw()

            elif event_match_kmi(self, event, "constraint_x"):
                if self.constraint_axis == (False, True):
                    self.constraint_axis = (False, False)
                    context.window.cursor_modal_set('HAND')
                else:
                    self.constraint_axis = (False, True)
                    context.window.cursor_modal_set('MOVE_X')

                self.build_shader_batch()
                context.region.tag_redraw()

            elif event_match_kmi(self, event, "flip_x"):
                self.bg.use_flip_x = not self.bg.use_flip_x

            elif event_match_kmi(self, event, "flip_y"):
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
        self.bg.offset[0] = self.init_bg_offset_x
        self.bg.offset[1] = self.init_bg_offset_y
        self.bg.use_flip_x = self.init_bg_flip_x
        self.bg.use_flip_y = self.init_bg_flip_y

    def finish_modal(self, context):
        context.area.header_text_set(text=None)
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.window.cursor_modal_restore()

    def build_shader_batch(self):

        def get_offset_co(mx, offset):
            offset_vec = Vector(offset)
            offset_mx = mx @ Matrix.Translation(offset_vec)
            offset_co = offset_mx.translation
            return offset_co

        draw_offset = Vector((0, 0, -2))
        draw_center_mx = self.cam.matrix_world @ Matrix.Translation(draw_offset)

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

        self.batch = batch_for_shader(shader, 'LINES', {"pos": co})

    def draw_constraint(self):
        if self.constraint_axis[0]:
            color = (0, 1, 0, 1)
        elif self.constraint_axis[1]:
            color = (1, 0, 0, 1)
        else:
            return

        shader.bind()
        shader.uniform_float("color", color)
        self.batch.draw(shader)


classes = (
    CAMERA_OT_background_move,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
