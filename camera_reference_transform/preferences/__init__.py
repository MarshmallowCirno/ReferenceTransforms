from . import addon_preferences, properties

_classes = (
    properties.ModalKeyMapItem,
    properties.AddonKeyMap,
    addon_preferences.ModalBackgroundTransformPreferences,
)


def register():
    from bpy.utils import register_class

    for cls in _classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(_classes):
        unregister_class(cls)
