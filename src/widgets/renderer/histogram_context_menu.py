import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.widgets.renderer.renderer_widget import RendererWidget


class HistogramContextMenu(tk.Menu):
    """The context menu that appears when you right click the histogram in the Render Configuration."""

    def __init__(self, render_widget: "RendererWidget", xdata: float):
        """Construct a HistogramContextMenu.

        :param render_widget: the owning render widget
        :param xdata: the x position of the cursor at the click relative to the axes
        """
        super().__init__(render_widget, tearoff=0)
        self.render_widget = render_widget
        self.xdata = xdata

        self.add_command(label="Copy value", command=self.copy_value)
        self.add_command(label="Set Min to this value", command=self.set_min)
        self.add_command(label="Set Max to this value", command=self.set_max)

    def copy_value(self):
        self.copy_to_clipboard(str(self.xdata))

    def set_min(self):
        self.render_widget.min_entry.delete(0, tk.END)
        self.render_widget.min_entry.insert(0, str(self.xdata))
        self.render_widget.on_entry_focusout(None)

    def set_max(self):
        self.render_widget.max_entry.delete(0, tk.END)
        self.render_widget.max_entry.insert(0, str(self.xdata))
        self.render_widget.on_entry_focusout(None)

    def copy_to_clipboard(self, text):
        """Copy text to the clipboard.

        :param text: what to copy
        """
        self.render_widget.clipboard_clear()
        self.render_widget.clipboard_append(text)
        self.render_widget.update()
