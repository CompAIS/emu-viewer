import tkinter as tk
from typing import Optional, TypeVar

from src import constants

T = TypeVar("T")


def with_defaults(*values: list[T]) -> Optional[T]:
    """Takes a list of values, returning the first one which is not None.

    :return: the first non-None argument, or None
    """

    for value in values:
        if value is not None:
            return value

    return None


def index_default(arr: list[T], index: int, default: T) -> T:
    """Does arr[index] by returning the given default if `index` is OOB."""

    return arr[index] if 0 <= index < len(arr) else default


def get_size_inches(widget: tk.Widget):
    """Returns the size of the given widget as a tuple of inches."""

    return widget.winfo_width() / constants.DPI, widget.winfo_height() / constants.DPI
