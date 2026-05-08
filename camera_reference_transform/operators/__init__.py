from . import background_move, background_rotate, background_scale

_classes = (
    background_move.CAMERA_OT_background_move,
    background_rotate.CAMERA_OT_background_rotate,
    background_scale.CAMERA_OT_background_scale,
)


def register() -> None:
    from bpy.utils import register_class

    for cls in _classes:
        register_class(cls)


def unregister() -> None:
    from bpy.utils import unregister_class

    for cls in _classes:
        unregister_class(cls)
