# ruff: noqa: F401
# pyright: reportUnusedImport = false
bl_info = {
    "name": "Reference Transforms",
    "author": "Cirno",
    "version": (1, 1),
    "blender": (4, 0, 0),
    "location": "Shortcuts in the addon preferences",
    "description": "Adjust camera background image scale, offset and rotation",
    "warning": "",
    "doc_url": "https://gumroad.com/l/rfstk",
    "tracker_url": "https://blenderartists.org/t/references-matching-setting-transforms-and-opacity-of-backgroud-images/1417682",
    "category": "Camera",
}


_RELOADABLE_MODULE_NAMES = (
    "package",
    "properties",
    "addon_preferences",
    "preferences",
    "keymaps",
    "modal_utils",
    "background_move",
    "background_rotate",
    "background_scale",
    "operators",
)

# Support reloading submodules
if "bpy" in locals():
    import importlib

    for module_name in _RELOADABLE_MODULE_NAMES:
        if module_name in locals():
            importlib.reload(locals()[module_name])

else:
    import bpy

    # Prevent imports when run in the background, since gpu shaders will not be available
    if not bpy.app.background:
        import operators
        import package
        import preferences

        from .operators import background_move, background_rotate, background_scale, keymaps, modal_utils
        from .preferences import addon_preferences, properties

import bpy  # noqa: E402

# Prevent loading in the background, since gpu shaders will not be available
if not bpy.app.background:
    from . import operators, preferences

    def register():
        preferences.register()
        operators.register()

    def unregister():
        preferences.unregister()
        operators.unregister()
