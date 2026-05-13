from . import ot_keymap, ot_move_background, ot_rotate_background, ot_scale_background

_classes = (
    ot_move_background.CAMERA_OT_move_background,
    ot_rotate_background.CAMERA_OT_rotate_background,
    ot_scale_background.CAMERA_OT_scale_background,
)


def register() -> None:
    from bpy.utils import register_class

    for cls in _classes:
        register_class(cls)

    ot_keymap.register()


def unregister() -> None:
    from bpy.utils import unregister_class

    for cls in _classes:
        unregister_class(cls)

    ot_keymap.unregister()
