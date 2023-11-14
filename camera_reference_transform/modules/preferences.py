import bpy
import rna_keymap_ui

from .keymaps import addon_keymaps
from .properties import AddonKeyMap
from ..package import get_addon_name


class ModalBackgroundTransform(bpy.types.AddonPreferences):
    bl_idname = get_addon_name()

    keymaps: bpy.props.CollectionProperty(type=AddonKeyMap)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        col.label(text="How to Use:")
        col.label(text="Activate a camera with a background, select it, use addon shortcuts and move "
                       "the mouse in horizontal directions.")

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Shortcuts for operators:")
        self.draw_keymap_items(col, "Object Mode", addon_keymaps, False)

        box = layout.box()
        col = box.column(align=True)
        col.label(text="Shortcuts in modal:")
        keymap_items = self.keymaps["modal"].keymap_items
        self.draw_modal_keymap_items(keymap_items=keymap_items, tag="Default", column=col)
        col.separator()
        self.draw_modal_keymap_items(keymap_items=keymap_items, tag="Mode", column=col)
        col.separator()
        self.draw_modal_keymap_items(keymap_items=keymap_items, tag="Reset", column=col)

    @staticmethod
    def draw_keymap_items(col, km_name, keymap, allow_remove):
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get(km_name)
        kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
        if allow_remove:
            col.context_pointer_set("keymap", km)

        kmis = [kmi for kmi in km.keymap_items if
                kmi.idname in kmi_idnames]
        for kmi in kmis:
            rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)

    @staticmethod
    def draw_modal_keymap_items(keymap_items, tag, column):

        for kmi in keymap_items.values():
            if kmi.tag == tag:
                row = column.row()
                row.use_property_split = True
                row.use_property_decorate = False
                row.prop(kmi, "type", text=kmi.label, event=True)

                row.alignment = 'RIGHT'
                row.prop(kmi, "alt", text='Alt', toggle=True)
                row.prop(kmi, "ctrl", text='Ctrl', toggle=True)
                row.prop(kmi, "shift", text='Shift', toggle=True)


classes = (
    ModalBackgroundTransform,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
