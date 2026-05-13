from typing import TYPE_CHECKING

import bpy
import rna_keymap_ui

from camera_reference_transform import addon_info

from ..operators import ot_keymap
from . import properties

if TYPE_CHECKING:
    ModalKeyMapItems = bpy.types.bpy_prop_collection_idprop[properties.ModalKeyMapItem]


class ModalBackgroundTransformPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_info.get_addon_package()

    if TYPE_CHECKING:
        modal_keymap_items: bpy.types.bpy_prop_collection_idprop[properties.ModalKeyMapItem]
    else:
        modal_keymap_items: bpy.props.CollectionProperty(type=properties.ModalKeyMapItem)

    def draw(self, _context: bpy.types.Context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        col.label(text="How to Use:")
        col.label(
            text="Activate a camera with a background, select it, use addon shortcuts and move "
            "the mouse in horizontal directions."
        )

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Shortcuts for operators:")
        self.draw_keymap_items(col, "Object Mode", ot_keymap.object_mode_keymap, False)

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Shortcuts in modal:")

        self.draw_modal_keymap_items(keymap_items=self.modal_keymap_items, column=col)

    @staticmethod
    def draw_keymap_items(
        col: bpy.types.UILayout,
        km_name: str,
        keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]],
        allow_remove: bool = False,
    ):
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get(km_name)
        kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
        if allow_remove:
            col.context_pointer_set("keymap", km)

        kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames]
        for kmi in kmis:
            rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)

    @staticmethod
    def draw_modal_keymap_items(
        keymap_items: "ModalKeyMapItems",
        column: bpy.types.UILayout,
    ):

        for kmi in keymap_items.values():
            row = column.row()
            row.use_property_split = True
            row.use_property_decorate = False
            row.prop(kmi, "type", text=kmi.label, event=True)

            row.alignment = 'RIGHT'
            row.prop(kmi, "alt", text='Alt', toggle=True)
            row.prop(kmi, "ctrl", text='Ctrl', toggle=True)
            row.prop(kmi, "shift", text='Shift', toggle=True)
