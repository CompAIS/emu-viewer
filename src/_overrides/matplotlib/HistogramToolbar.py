import os.path
import tkinter as tk
import tkinter.font

import numpy as np
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from PIL import Image, ImageTk

from src.constants import ASSETS_FOLDER

# Note from us before you go into the depths below.
#
# We did this for the following reasons:
# - to lock the histogram to the x-axes
# - to override the tooltip to only show the current x-value
# - to remove some buttons (subplot settings)
# -----


class HistogramToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent, pack):
        # Edit toolitems to add new actions to toolbar
        # format of new tool is:
        # (
        #   text, # the text of the button (often not visible to users)
        #   tooltip_text, # the tooltip shown on hover (where possible)
        #   image_file, # name of the image for the button (without the extension)
        #   name_of_function, # name of the method in NavigationToolbar to call
        # )

        self.toolitems = (
            ("Home", "Reset original view", "home", "home"),
            ("Back", "Back to previous view", "back", "back"),
            ("Forward", "Forward to next view", "forward", "forward"),
            (None, None, None, None),
            (
                "Pan",
                "Left button pans, Right button zooms\n"
                "x/y fixes axis, CTRL fixes aspect",
                "move",
                "pan",
            ),
            ("Zoom", "Zoom to rectangle\nx/y fixes axis", "zoom_to_rect", "zoom"),
            (None, None, None, None),
            ("Save", "Save the figure", "filesave", "save_figure"),
        )
        self.check_vars = {}

        super().__init__(canvas, parent, pack_toolbar=pack)

    def drag_pan(self, event):
        """Callback for dragging in pan/zoom mode."""
        for ax in self._pan_info.axes:
            # Using the recorded button at the press is safer than the current
            # button, as multiple buttons can get pressed during motion.
            # Changed for histogram functionality, forced event key to be x
            ax.drag_pan(self._pan_info.button, "x", event.x, event.y)
        self.canvas.draw_idle()

    def drag_zoom(self, event):
        """Callback for dragging in zoom mode."""
        start_xy = self._zoom_info.start_xy
        ax = self._zoom_info.axes[0]
        (x1, y1), (x2, y2) = np.clip(
            [start_xy, [event.x, event.y]], ax.bbox.min, ax.bbox.max
        )
        # Changed for histogram functionality, forced event key to be x
        key = "x"
        # Force the key on colorbars to extend the short-axis bbox
        if self._zoom_info.cbar == "horizontal":
            key = "x"
        elif self._zoom_info.cbar == "vertical":
            key = "y"
        if key == "x":
            y1, y2 = ax.bbox.intervaly
        elif key == "y":
            x1, x2 = ax.bbox.intervalx

        self.draw_rubberband(event, x1, y1, x2, y2)

    def release_zoom(self, event):
        """Callback for mouse button release in zoom to rect mode."""
        if self._zoom_info is None:
            return

        # We don't check the event button here, so that zooms can be cancelled
        # by (pressing and) releasing another mouse button.
        self.canvas.mpl_disconnect(self._zoom_info.cid)
        self.remove_rubberband()

        start_x, start_y = self._zoom_info.start_xy
        # Changed for histogram functionality, forced event key to be x
        key = "x"
        # Force the key on colorbars to ignore the zoom-cancel on the
        # short-axis side
        if self._zoom_info.cbar == "horizontal":
            key = "x"
        elif self._zoom_info.cbar == "vertical":
            key = "y"
        # Ignore single clicks: 5 pixels is a threshold that allows the user to
        # "cancel" a zoom action by zooming by less than 5 pixels.
        if (abs(event.x - start_x) < 5 and key != "y") or (
            abs(event.y - start_y) < 5 and key != "x"
        ):
            self.canvas.draw_idle()
            self._zoom_info = None
            return

        for i, ax in enumerate(self._zoom_info.axes):
            # Detect whether this Axes is twinned with an earlier Axes in the
            # list of zoomed Axes, to avoid double zooming.
            twinx = any(
                ax.get_shared_x_axes().joined(ax, prev)
                for prev in self._zoom_info.axes[:i]
            )
            twiny = any(
                ax.get_shared_y_axes().joined(ax, prev)
                for prev in self._zoom_info.axes[:i]
            )
            ax._set_view_from_bbox(
                (start_x, start_y, event.x, event.y),
                self._zoom_info.direction,
                key,
                twinx,
                twiny,
            )

        self.canvas.draw_idle()
        self._zoom_info = None
        self.push_current()

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for text, mode in [
            ("Zoom", "zoom rect"),
            ("Pan", "pan/zoom"),
        ]:
            if text in self._buttons:
                if self.mode == mode:
                    self.check_vars[text].set(1)
                else:
                    self.check_vars[text].set(0)

    def _Button(self, text, image_file, toggle, command):
        if not toggle:
            b = tb.Button(master=self, text=text, command=command, bootstyle="primary")
        else:
            # There is a bug in tkinter included in some python 3.6 versions
            # that without this variable, produces a "visual" toggling of
            # other near checkbuttons
            # https://bugs.python.org/issue29402
            # https://bugs.python.org/issue25684
            var = tk.IntVar(master=self)
            b = tb.Checkbutton(
                master=self,
                text=text,
                command=command,
                variable=var,
                bootstyle="toolbutton-light",
            )
            b.var = var
            self.check_vars[text] = var
        b._image_file = image_file
        if image_file is not None:
            HistogramToolbar._set_image_for_button(self, b)
        else:
            b.configure(font=self._label_font)
        b.pack(side=tk.LEFT)
        return b

    def _set_image_for_button(self, button):
        style = tb.Style()
        if button._image_file is None:
            return

        path_regular = os.path.join(ASSETS_FOLDER, button._image_file)
        size = button.winfo_pixels("12p")

        # Nested functions because ToolbarTk calls  _Button.
        def _get_color(color_name):
            # `winfo_rgb` returns an (r, g, b) tuple in the range 0-65535
            return style.colors.hex_to_rgb(style.colors.get(color_name))

        def _is_dark(color):
            if isinstance(color, str):
                color = _get_color(color)
            return max(color) < 65535 / 2

        def _recolor_icon(image, color):
            image_data = np.asarray(image).copy()
            black_mask = (image_data[..., :3] == 0).all(axis=-1)
            image_data[black_mask, :3] = color
            return Image.fromarray(image_data, mode="RGBA")

        # Use the high-resolution (48x48 px) icon if it exists and is needed
        with Image.open(path_regular) as im:
            # assure a RGBA image as foreground color is RGB
            im = im.convert("RGBA")
            image = ImageTk.PhotoImage(im.resize((size, size)), master=self)
            button._ntimage = image

            # create a version of the icon with the button's text color
            foreground = (255 / 65535) * np.array(
                style.colors.hex_to_rgb(style.colors.get("fg"))
            )
            im_alt = _recolor_icon(im, foreground)
            image_alt = ImageTk.PhotoImage(im_alt.resize((size, size)), master=self)
            button._ntimage_alt = image_alt

        if _is_dark("bg"):
            image_kwargs = {"image": image_alt}
        else:
            image_kwargs = {"image": image}

        button.configure(**image_kwargs)
