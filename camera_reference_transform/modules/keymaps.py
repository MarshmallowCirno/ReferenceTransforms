import bpy

from ..package import get_preferences

addon_keymaps = []


def register_modal_keymap():
    modal_keymap = get_preferences().keymaps.get("modal")
    if modal_keymap is None:
        modal_keymap = get_preferences().keymaps.add()
        modal_keymap.name = "modal"

        keymap_items = modal_keymap.keymap_items

        kmi = keymap_items.add()
        kmi.name = "constraint_x"
        kmi.label = "Constraint X"
        kmi.type = 'X'
        kmi.tag = "Default"

        kmi = keymap_items.add()
        kmi.name = "constraint_y"
        kmi.label = "Constraint Y"
        kmi.type = 'Y'
        kmi.tag = "Default"

        kmi = keymap_items.add()
        kmi.name = "flip_x"
        kmi.label = "Flip Image X"
        kmi.type = 'H'
        kmi.tag = "Default"

        kmi = keymap_items.add()
        kmi.name = "flip_y"
        kmi.label = "Flip Image Y"
        kmi.type = 'V'
        kmi.tag = "Default"


def register():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')

        kmi = km.keymap_items.new("camera.background_scale", 'S', 'PRESS', alt=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("camera.background_move", 'G', 'PRESS', alt=True, ctrl=True)
        addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new("camera.background_rotate", 'R', 'PRESS', alt=True, ctrl=True)
        addon_keymaps.append((km, kmi))

    register_modal_keymap()


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
