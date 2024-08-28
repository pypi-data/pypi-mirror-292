import platform
import subprocess
import logging
from typing import Optional

logger = logging.getLogger("labelsmith")

def get_modifier_key() -> str:
    """
    Get the appropriate modifier key based on the operating system.

    Returns:
        str: 'Command' for macOS, 'Control' for other operating systems.
    """
    return "Command" if platform.system() == "Darwin" else "Control"

def modkey_backspace(event) -> str:
    """
    Handle the modifier key + backspace event to delete one word.

    Args:
        event: The event object.

    Returns:
        str: 'break' to prevent further processing of the event.
    """
    widget = event.widget
    if isinstance(widget, tk.Text):
        # Delete the word before the cursor
        widget.delete("insert-1c wordstart", "insert")
    elif isinstance(widget, tk.Entry):
        # Get current cursor position
        cursor_position = widget.index(tk.INSERT)
        # Find the start of the word
        word_start = cursor_position
        while word_start > 0 and widget.get()[word_start-1:word_start].isalnum():
            word_start -= 1
        # Delete from word start to cursor position
        widget.delete(word_start, cursor_position)
    else:
        logger.warning(f"Word delete operation not supported for widget type: {type(widget)}")
    return 'break'

def modkey_shift_backspace(event) -> str:
    """
    Handle the modifier key + shift + backspace event to delete the whole line.

    Args:
        event: The event object.

    Returns:
        str: 'break' to prevent further processing of the event.
    """
    widget = event.widget
    if isinstance(widget, tk.Text):
        # Delete the current line
        widget.delete("insert linestart", "insert lineend + 1c")
    elif isinstance(widget, tk.Entry):
        # For Entry widgets, delete all text as it's single-line
        widget.delete(0, tk.END)
    else:
        logger.warning(f"Line delete operation not supported for widget type: {type(widget)}")
    return 'break'