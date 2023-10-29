import tkinter as tk
from typing import List, Optional, TypeVar

T = TypeVar("T")


def with_defaults(*values: List[T]) -> Optional[T]:
    """Takes a list of values, returning the first one which is not None.

    :return: the first non-None argument, or None
    """

    for value in values:
        if value is not None:
            return value

    return None


def index_default(list: List[T], index: int, default: T) -> T:
    """Does list[index] by returning the given default if `index` is OOB."""

    return list[index] if index >= 0 and index < len(list) else default


def get_size_inches(widget: tk.Widget):
    """Returns the size of the given widget as a tuple of inches."""

    return widget.winfo_width() / DPI, widget.winfo_height() / DPI
