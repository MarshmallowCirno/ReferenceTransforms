from typing import TYPE_CHECKING

import bpy

modal_key_items = []
modal_key_names = {}
for i in bpy.types.Event.bl_rna.properties["type"].enum_items.values():
    modal_key_items.append((i.identifier, i.name, "", i.value))
    modal_key_names[i.identifier] = i.description or i.name


class ModalKeyMapItem(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        label: str
        tag: str
        type: str
        alt: bool
        ctrl: bool
        shift: bool
    else:
        label: bpy.props.StringProperty()
        tag: bpy.props.StringProperty()
        type: bpy.props.EnumProperty(
            name="Type",
            description="Type of event",
            items=modal_key_items,
        )
        alt: bpy.props.BoolProperty(description="Alt key pressed", name="Alt", default=False)
        ctrl: bpy.props.BoolProperty(description="Control key pressed", name="Ctrl", default=False)
        shift: bpy.props.BoolProperty(description="Shift key pressed", name="Shift", default=False)


class AddonKeyMap(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        keymap_items: bpy.types.bpy_prop_collection_idprop[ModalKeyMapItem]
    else:
        keymap_items: bpy.props.CollectionProperty(type=ModalKeyMapItem)
