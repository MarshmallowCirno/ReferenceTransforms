import bpy

from camera_reference_transform import addon_info

object_mode_keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []


def _populate_addon_preferences_modal_keymap():
    keymap_items = addon_info.get_preferences().modal_keymap_items

    if "constraint_x" not in keymap_items:
        kmi = keymap_items.add()
        kmi.name = "constraint_x"
        kmi.label = "Constraint X"
        kmi.type = 'X'

    if "constraint_y" not in keymap_items:
        kmi = keymap_items.add()
        kmi.name = "constraint_y"
        kmi.label = "Constraint Y"
        kmi.type = 'Y'

    if "flip_x" not in keymap_items:
        kmi = keymap_items.add()
        kmi.name = "flip_x"
        kmi.label = "Flip Image X"
        kmi.type = 'H'

    if "flip_y" not in keymap_items:
        kmi = keymap_items.add()
        kmi.name = "flip_y"
        kmi.label = "Flip Image Y"
        kmi.type = 'V'


def register():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')

        kmi = km.keymap_items.new("camera.background_scale", 'S', 'PRESS', alt=True, ctrl=True)
        object_mode_keymap.append((km, kmi))

        kmi = km.keymap_items.new("camera.background_move", 'G', 'PRESS', alt=True, ctrl=True)
        object_mode_keymap.append((km, kmi))

        kmi = km.keymap_items.new("camera.background_rotate", 'R', 'PRESS', alt=True, ctrl=True)
        object_mode_keymap.append((km, kmi))

    _populate_addon_preferences_modal_keymap()


def unregister():
    for km, kmi in object_mode_keymap:
        km.keymap_items.remove(kmi)
    object_mode_keymap.clear()
