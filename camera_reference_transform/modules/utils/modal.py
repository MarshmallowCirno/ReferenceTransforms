def event_match_kmi(operator, event, idname: str, release: bool = False) -> bool:
    """Return match between event type and keymap item type."""
    if release:
        return event.type == operator.keymap_items[idname].type
    else:
        return (event.type == (kmi := operator.keymap_items[idname]).type
                and event.alt == kmi.alt
                and event.ctrl == kmi.ctrl
                and event.shift == kmi.shift)
