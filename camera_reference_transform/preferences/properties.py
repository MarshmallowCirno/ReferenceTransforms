from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

import bpy


def _yield_event_type_enum_property_items() -> Iterable[tuple[str, str, str, int]]:
    # https://docs.blender.org/api/current/bpy_types_enum_items/event_type_items.html
    event_type_enum = cast(bpy.types.EnumProperty, bpy.types.Event.bl_rna.properties["type"])
    for event_type_enum_item in event_type_enum.enum_items.values():
        if event_type_enum_item is None:
            continue
        yield (
            # https://docs.blender.org/api/current/bpy.props.html#bpy.props.EnumProperty
            # identifier
            event_type_enum_item.identifier,
            # name
            event_type_enum_item.name,
            # description
            "",
            # number
            event_type_enum_item.value,
        )


class ModalKeyMapItem(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        label: str
        type: str
        alt: bool
        ctrl: bool
        shift: bool
    else:
        # Label of the keymap item to draw in input field in preferences.
        label: bpy.props.StringProperty()
        # Value of the keymap item, i.e. Event type.
        type: bpy.props.EnumProperty(
            name="Type",
            description="Type of event",
            items=(*_yield_event_type_enum_property_items(),),
        )
        alt: bpy.props.BoolProperty(description="Alt key pressed", name="Alt", default=False)
        ctrl: bpy.props.BoolProperty(description="Control key pressed", name="Ctrl", default=False)
        shift: bpy.props.BoolProperty(description="Shift key pressed", name="Shift", default=False)


class AddonKeyMap(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        keymap_items: bpy.types.bpy_prop_collection_idprop[ModalKeyMapItem]
    else:
        keymap_items: bpy.props.CollectionProperty(type=ModalKeyMapItem)
