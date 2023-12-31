import tkinter as tk

from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog


class ColourChooserButton(tk.Canvas):
    """A button which will bring up a dialogue for the user to choose a colour.

    The button's colour will change depending on the currently selected colour.
    """

    def __init__(
        self,
        master: tk.Widget,
        width: int,
        height: int,
        window_title: str,
        default: str = "#03fc49",
        variable: tk.StringVar = None,
    ):
        """Construct a ColourChooserButton.

        :param master: parent of this widget
        :param width: width of the button in pixels
        :param height: height of the button in pixels
        :param window_title: title of the popup window
        :param default: the default colour for the canvas
        """
        super().__init__(master, width=width, height=height, bg=default)

        self.master = master
        self.window_title = window_title
        self.variable = variable
        self.selected_colour = (
            default
            if self.variable is None or self.variable.get() == ""
            else self.variable.get()
        )

        self.rect = self.create_rectangle(
            0, 0, width - 1, height - 1, outline="black", fill=self.selected_colour
        )

        self.set_selected_colour(self.selected_colour)

        self.bind("<Button-1>", self.on_click)
        self.config(cursor="hand2")

    def get(self) -> str:
        """Get the currently selected colour."""
        return self.selected_colour

    def set_selected_colour(self, colour: str):
        """Set the current selected colour manually."""
        self.selected_colour = colour
        self.itemconfig(self.rect, fill=self.selected_colour)
        if self.variable is not None:
            self.variable.set(colour)

    def on_click(self, _event):
        """Handler for when the user clicks this button."""

        cd = ColorChooserDialog(
            initialcolor=self.selected_colour, title=self.window_title
        )
        cd.show()

        # return focus to the owning window
        self.after(1, lambda: self.master.focus_set())

        # on cancel for e.g.
        if cd.result is None:
            return

        self.set_selected_colour(cd.result.hex)
