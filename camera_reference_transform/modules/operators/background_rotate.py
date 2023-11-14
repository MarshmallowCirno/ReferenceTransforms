from typing import Optional

from math import degrees
from math import radians

import bpy
from bpy.types import CameraBackgroundImage
from bpy.types import Object

from ...package import get_preferences
from ..properties import ModalKeyMapItem
from ..utils.modal import event_match_kmi


class CAMERA_OT_background_rotate(bpy.types.Operator):
    """Rotate camera background image"""

    bl_idname = "camera.background_rotate"
    bl_label = "Rotate Camera Background"
    bl_options = {'REGISTER', 'UNDO', 'GRAB_CURSOR', 'BLOCKING'}

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

        self.bg_rotation_float: float = 0

        self.init_bg_rotation: int = 0
        self.init_bg_offset_x: int = 0
        self.init_bg_offset_y: int = 0
        self.init_bg_flip_x: bool = False
        self.init_bg_flip_y: bool = False

    def invoke(self, context, event):
        self.cam = context.object
        cam_backgrounds = [bg for bg in self.cam.data.background_images if bg.image and bg.show_background_image]
        if not any(cam_backgrounds):
            self.report({'WARNING'}, "No visible backgrounds")
            return {'CANCELLED'}

        self.bg = cam_backgrounds[0]
        self.last_mouse_x = event.mouse_region_x

        self.init_bg_rotation = self.bg_rotation_float = self.bg.rotation
        self.init_bg_flip_x = self.bg.use_flip_x
        self.init_bg_flip_y = self.bg.use_flip_y

        self.redraw_status(context)
        context.window.cursor_modal_set('MOVE_X')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def redraw_status(self, context) -> None:
        """Draw shortcuts in the status."""
        flip_x_key = self.keymap_items["flip_x"].type
        flip_y_key = self.keymap_items["flip_y"].type

        status_text = (
            f"LMB, ENTER: Confirm | "
            f"RMB, ESC: Cancel | "
            f"{flip_x_key}: Flip Horizontally | "
            f"{flip_y_key}: Flip Vertically"
        )
        context.workspace.status_text_set(status_text)

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            mouse_x = event.mouse_region_x
            mouse_offset_x = mouse_x - self.last_mouse_x

            divisor = 4500 if event.shift else 450
            offset = mouse_offset_x / divisor
            self.bg_rotation_float += offset

            if event.ctrl or (context.scene.tool_settings.use_snap
                              and context.scene.tool_settings.use_snap_scale
                              and context.scene.tool_settings.snap_elements == 'INCREMENT'
                              and not event.ctrl):
                rounded = radians(round(degrees(self.bg_rotation_float) / 15) * 15)
                if self.bg.rotation != rounded:
                    self.bg.rotation = rounded
            else:
                self.bg.rotation = self.bg_rotation_float

            context.area.header_text_set(f"Background Rotation: {degrees(self.bg.rotation):.2f}°")

            self.last_mouse_x = event.mouse_region_x

        if event.value == 'PRESS':
            if event_match_kmi(self, event, "flip_x"):
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
        self.bg.rotation = self.init_bg_rotation
        self.bg.use_flip_x = self.init_bg_flip_x
        self.bg.use_flip_y = self.init_bg_flip_y

    @staticmethod
    def finish_modal(context):
        context.area.header_text_set(text=None)
        context.workspace.status_text_set(text=None)
        context.window.cursor_modal_restore()


classes = (
    CAMERA_OT_background_rotate,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
