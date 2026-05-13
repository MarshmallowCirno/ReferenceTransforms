from typing import TYPE_CHECKING, cast

import bpy

if TYPE_CHECKING:
    from .preferences.addon_preferences import ModalBackgroundTransformPreferences


def get_preferences() -> "ModalBackgroundTransformPreferences":
    assert isinstance(__package__, str)
    return cast("ModalBackgroundTransformPreferences", bpy.context.preferences.addons[__package__].preferences)


def get_addon_package() -> str:
    """Return the name of the addon package."""
    assert isinstance(__package__, str)
    return __package__
