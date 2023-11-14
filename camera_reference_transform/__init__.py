bl_info = {
    "name": "Reference Transforms",
    "author": "Cirno",
    "version": (1, 1),
    "blender": (4, 0, 0),
    "location": "Shortcuts in the addon preferences",
    "description": "Adjust camera background image scale, offset and rotation",
    "warning": "",
    "doc_url": "https://gumroad.com/l/rfstk",
    "tracker_url": "https://blenderartists.org/t/references-matching-setting-transforms-and-opacity-of-backgroud"
                   "-images/1417682",
    "category": "Camera",
}


reloadable_modules = (
    "keymaps",
    "properties",
    "preferences",
    "background_move",
    "background_rotate",
    "background_scale",
)


# when bpy is already in local, we know this is not the initial import,
# so we need to reload our submodule(s) using importlib.
if "bpy" in locals():
    import importlib

    # reload modules twice so modules that import from other modules
    # always get stuff that's up-to-date.
    for _ in range(2):
        for module in reloadable_modules:
            if module in locals():
                importlib.reload(locals()[module])
else:
    from .modules import properties
    from .modules import preferences
    from .modules.operators import background_move
    from .modules.operators import background_rotate
    from .modules.operators import background_scale
    from .modules import keymaps


import bpy


def register():
    properties.register()
    preferences.register()
    background_move.register()
    background_rotate.register()
    background_scale.register()
    keymaps.register()


def unregister():
    keymaps.unregister()
    background_move.unregister()
    background_rotate.unregister()
    background_scale.unregister()
    preferences.unregister()
    properties.unregister()
