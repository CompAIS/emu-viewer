import os.path
import tkinter as tk
import tkinter.font
from collections import namedtuple
from functools import partial
from tkinter import simpledialog

import numpy as np
import ttkbootstrap as tb
from matplotlib.backend_bases import NavigationToolbar2
from matplotlib.backends._backend_tk import ToolTip
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from PIL import Image, ImageTk
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog

ASSETS_FOLDER = "./resources/assets"


class NavigationToolbar(NavigationToolbar2Tk):
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
            (
                "Line",
                "Draw line on figure",
                "line",
                "lock_line",
            ),
            (
                "Text",
                "Add text to figure",
                "type",
                "lock_text",
            ),
            (
                "Erase",
                "Erase figure annotations",
                "erase",
                "lock_erase",
            ),
            (None, None, None, None),
            (
                "Settings",
                "Configure annotation settings",
                "settings",
                "annotation_settings",
            ),
            ("Save", "Save the figure", "filesave", "save_figure"),
        )

        self._line_info = None
        self._erase_info = None

        self.super_init(canvas, parent)

        self.prev_x = None
        self.prev_y = None

        self.line_size = 5
        self.line_colour = "red"
        self.text_size = 5
        self.text_colour = "red"
        self.erase_size = 5

    def super_init(self, canvas, window):
        if window is None:
            window = canvas.get_tk_widget().master
        tk.Frame.__init__(
            self,
            master=window,
            borderwidth=2,
            width=int(canvas.figure.bbox.width),
            height=50,
        )

        self._buttons = {}
        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                # Add a spacer; return value is unused.
                self._Spacer()
            else:
                self._buttons[text] = button = self._Button(
                    text,
                    # Modified for custom images
                    str(f"{image_file}.png"),
                    # Modified to allow for custom toggled buttons
                    toggle=callback
                    in ["zoom", "pan", "lock_line", "lock_text", "lock_erase"],
                    command=getattr(self, callback),
                )
                if tooltip_text is not None:
                    ToolTip.createToolTip(button, tooltip_text)

        self._label_font = tkinter.font.Font(root=window, size=10)

        # This filler item ensures the toolbar is always at least two text
        # lines high. Otherwise the canvas gets redrawn as the mouse hovers
        # over images because those use two-line messages which resize the
        # toolbar.
        label = tk.Label(
            master=self,
            font=self._label_font,
            # Adjusted to add 4 lines to cover all different coordinates
            text="\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}",
        )
        label.pack(side=tk.RIGHT)

        self.message = tk.StringVar(master=self)
        self._message_label = tk.Label(
            master=self,
            font=self._label_font,
            textvariable=self.message,
            justify=tk.RIGHT,
        )
        self._message_label.pack(side=tk.RIGHT)

        NavigationToolbar2.__init__(self, canvas)

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for text, mode in [
            ("Zoom", "zoom rect"),
            ("Pan", "pan/zoom"),
            ("Line", "line_tool"),
            ("Text", "text_tool"),
            ("Erase", "erase_tool"),
        ]:
            if text in self._buttons:
                if self.mode == mode:
                    self._buttons[text].select()  # NOT .invoke()
                else:
                    self._buttons[text].deselect()

    def _zoom_pan_handler(self, event):
        if self.mode == "pan/zoom":
            if event.name == "button_press_event":
                self.press_pan(event)
            elif event.name == "button_release_event":
                self.release_pan(event)
        if self.mode == "zoom rect":
            if event.name == "button_press_event":
                self.press_zoom(event)
            elif event.name == "button_release_event":
                self.release_zoom(event)
        if self.mode == "line_tool":
            if event.name == "button_press_event":
                self.press_line(event)
            elif event.name == "button_release_event":
                self.release_line(event)
        if self.mode == "text_tool":
            if event.name == "button_press_event":
                self.press_text(event)
            elif event.name == "button_release_event":
                self.release_text(event)
        if self.mode == "erase_tool":
            if event.name == "button_press_event":
                self.press_erase(event)
            elif event.name == "button_release_event":
                self.release_erase(event)

    def lock_line(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("line tool unavailable")
            return
        if self.mode == "line_tool":
            self.mode = ""
            self.canvas.widgetlock.release(self)
        else:
            self.mode = "line_tool"
            self.canvas.widgetlock(self)
        self._update_buttons_checked()

    _LineInfo = namedtuple("_LineInfo", "button axes cid")

    def press_line(self, event):
        if event.button != 1 or event.x is None or event.y is None:
            return
        axes = [a for a in self.canvas.figure.get_axes() if a.in_axes(event)]
        if not axes:
            return
        self.canvas.mpl_disconnect(self._id_drag)
        id_drag = self.canvas.mpl_connect("motion_notify_event", self.draw_line)
        self._line_info = self._LineInfo(button=event.button, axes=axes, cid=id_drag)

    def draw_line(self, event):
        for ax in self._line_info.axes:
            if self.prev_x is None or self.prev_y is None:
                self.prev_x = event.xdata
                self.prev_y = event.ydata
                return

            ax.plot(
                [self.prev_x, event.xdata],
                [self.prev_y, event.ydata],
                color=self.line_colour,
                linewidth=self.line_size,
            )

            self.prev_x = event.xdata
            self.prev_y = event.ydata

        self.canvas.draw_idle()

    def release_line(self, event):
        if self._line_info is None:
            return
        self.canvas.mpl_disconnect(self._line_info.cid)
        self._id_drag = self.canvas.mpl_connect("motion_notify_event", self.mouse_move)
        self.canvas.draw_idle()
        self._line_info = None
        self.prev_x = None
        self.prev_y = None

    def lock_text(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("text tool unavailable")
            return
        if self.mode == "text_tool":
            self.mode = ""
            self.canvas.widgetlock.release(self)
        else:
            self.mode = "text_tool"
            self.canvas.widgetlock(self)
        self._update_buttons_checked()

    def press_text(self, event):
        if event.button != 1 or event.x is None or event.y is None:
            return
        axes = [a for a in self.canvas.figure.get_axes() if a.in_axes(event)]
        if not axes:
            return

        text = simpledialog.askstring("Type on Figure", "Enter text:")

        if text is None:
            return

        for ax in axes:
            ax.text(
                event.xdata,
                event.ydata,
                text,
                fontsize=self.text_size,
                color=self.text_colour,
            )

        self.canvas.draw_idle()

    def release_text(self, event):
        self.canvas.draw_idle()

    def lock_erase(self):
        if not self.canvas.widgetlock.available(self):
            self.set_message("erase tool unavailable")
            return
        if self.mode == "erase_tool":
            self.mode = ""
            self.canvas.widgetlock.release(self)
        else:
            self.mode = "erase_tool"
            self.canvas.widgetlock(self)
        self._update_buttons_checked()

    _EraseInfo = namedtuple("_EraseInfo", "button axes cid")

    def press_erase(self, event):
        if event.button != 1 or event.x is None or event.y is None:
            return
        axes = [a for a in self.canvas.figure.get_axes() if a.in_axes(event)]
        if not axes:
            return
        self.canvas.mpl_disconnect(self._id_drag)
        id_drag = self.canvas.mpl_connect("motion_notify_event", self.draw_erase)
        self._erase_info = self._EraseInfo(button=event.button, axes=axes, cid=id_drag)

    def draw_erase(self, event):
        for ax in self._erase_info.axes:
            for line in ax.lines:
                line.set_pickradius(self.erase_size)
                contains, lines_data = line.contains(event)
                if contains:
                    line.remove()

            for text in ax.texts:
                contains, texts_data = text.contains(event)
                if contains:
                    text.remove()

        self.canvas.draw_idle()

    def release_erase(self, event):
        if self._erase_info is None:
            return
        self.canvas.mpl_disconnect(self._erase_info.cid)
        self._id_drag = self.canvas.mpl_connect("motion_notify_event", self.mouse_move)
        self.canvas.draw_idle()
        self._erase_info = None
        self.prev_x = None
        self.prev_y = None

    def annotation_settings(
        self,
    ):
        config = tk.Toplevel(self)
        config.title("Annotation Config")
        config.resizable(False, False)

        config.columnconfigure(0, weight=1)
        config.rowconfigure(0, weight=1)

        frame = tb.Frame(config, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        config.columnconfigure((0, 1), weight=1)
        config.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        title_label = tb.Label(frame, text="Config Options", bootstyle="inverse-light")
        title_label.grid(
            column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10
        )

        # Size and colour config for line tool
        line_size_label = tb.Label(
            frame, text=f"Line Size ({self.line_size:1.2f})", bootstyle="inverse-light"
        )
        line_size_label.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        line_size_slider = tb.Scale(
            frame,
            from_=1,
            to=25,
            command=partial(self.set_line_size, line_size_label),
            value=self.line_size,
        )
        line_size_slider.grid(column=1, row=1, padx=10, pady=10, sticky=tk.NSEW)

        line_colour_label = tb.Label(
            frame, text="Line Colour", bootstyle="inverse-light"
        )
        line_colour_label.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)

        box_size = 23
        self.line_button = tk.Canvas(
            frame, bg=self.line_colour, width=box_size + 1, height=box_size + 1
        )
        self.line_button.grid(column=1, row=2, sticky=tk.W, padx=10, pady=10)
        self.line_rect = self.line_button.create_rectangle(
            0, 0, box_size, box_size, outline="black", fill=self.line_colour
        )
        self.line_button.bind("<Button-1>", self.set_line_colour)

        # Size and colour config for text tool
        text_size_label = tb.Label(
            frame, text=f"Text Size ({self.text_size:1.2f})", bootstyle="inverse-light"
        )
        text_size_label.grid(column=0, row=3, sticky=tk.NSEW, padx=10, pady=10)

        text_size_slider = tb.Scale(
            frame,
            from_=1,
            to=25,
            command=partial(self.set_text_size, text_size_label),
            value=self.text_size,
        )
        text_size_slider.grid(column=1, row=3, padx=10, pady=10, sticky=tk.NSEW)

        text_colour_label = tb.Label(
            frame, text="Text Colour", bootstyle="inverse-light"
        )
        text_colour_label.grid(column=0, row=4, sticky=tk.NSEW, padx=10, pady=10)

        box_size = 23
        self.text_button = tk.Canvas(
            frame, bg=self.line_colour, width=box_size + 1, height=box_size + 1
        )
        self.text_button.grid(column=1, row=4, sticky=tk.W, padx=10, pady=10)
        self.text_rect = self.text_button.create_rectangle(
            0, 0, box_size, box_size, outline="black", fill=self.text_colour
        )
        self.text_button.bind("<Button-1>", self.set_text_colour)

        # Size config for erase tool
        erase_size_label = tb.Label(
            frame,
            text=f"Erase Size ({self.erase_size:1.2f})",
            bootstyle="inverse-light",
        )
        erase_size_label.grid(column=0, row=5, sticky=tk.NSEW, padx=10, pady=10)

        erase_size_slider = tb.Scale(
            frame,
            from_=1,
            to=25,
            command=partial(self.set_erase_size, erase_size_label),
            value=self.erase_size,
        )
        erase_size_slider.grid(column=1, row=5, padx=10, pady=10, sticky=tk.NSEW)

        apply_button = tb.Button(
            frame,
            bootstyle="success",
            text="Apply",
            command=partial(self.apply_config, config),
        )
        apply_button.grid(column=1, row=6, sticky=tk.SE, padx=10, pady=10)

        config.grab_set()

    def set_line_size(self, size_label, value):
        value = float(value)
        self.line_size = value
        size_label["text"] = f"Line Size ({value:1.2f})"

    def set_line_colour(self, _evt):
        cd = ColorChooserDialog(
            initialcolor=self.line_colour, title="Choose line colour"
        )
        cd.show()
        self.after(1, lambda: self.focus_set())

        if cd.result is None:
            return

        self.line_colour = cd.result.hex
        self.line_button.itemconfig(self.line_rect, fill=self.line_colour)

    def set_text_size(self, size_label, value):
        value = float(value)
        self.text_size = value
        size_label["text"] = f"Text Size ({value:1.2f})"

    def set_text_colour(self, _evt):
        cd = ColorChooserDialog(
            initialcolor=self.text_colour, title="Choose line colour"
        )
        cd.show()
        self.after(1, lambda: self.focus_set())

        if cd.result is None:
            return

        self.text_colour = cd.result.hex
        self.text_button.itemconfig(self.text_rect, fill=self.text_colour)

    def set_erase_size(self, size_label, value):
        value = float(value)
        self.erase_size = value
        size_label["text"] = f"Erase Size ({value:1.2f})"

    def apply_config(self, config):
        config.destroy()

    def update_stack(self):
        self.push_current()

    # Overriding to allow for custom images
    def _Button(self, text, image_file, toggle, command):
        if not toggle:
            b = tk.Button(
                master=self,
                text=text,
                command=command,
                relief="flat",
                overrelief="groove",
                borderwidth=1,
            )
        else:
            # There is a bug in tkinter included in some python 3.6 versions
            # that without this variable, produces a "visual" toggling of
            # other near checkbuttons
            # https://bugs.python.org/issue29402
            # https://bugs.python.org/issue25684
            var = tk.IntVar(master=self)
            b = tk.Checkbutton(
                master=self,
                text=text,
                command=command,
                indicatoron=False,
                variable=var,
                offrelief="flat",
                overrelief="groove",
                borderwidth=1,
            )
            b.var = var
        b._image_file = image_file
        if image_file is not None:
            NavigationToolbar._set_image_for_button(self, b)
        else:
            b.configure(font=self._label_font)
        b.pack(side=tk.LEFT)
        return b

    def _set_image_for_button(self, button):
        if button._image_file is None:
            return

        path_regular = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "resources",
            "assets",
            button._image_file,
        )
        size = button.winfo_pixels("18p")

        # Nested functions because ToolbarTk calls  _Button.
        def _get_color(color_name):
            # `winfo_rgb` returns an (r, g, b) tuple in the range 0-65535
            return button.winfo_rgb(button.cget(color_name))

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
                button.winfo_rgb(button.cget("foreground"))
            )
            im_alt = _recolor_icon(im, foreground)
            image_alt = ImageTk.PhotoImage(im_alt.resize((size, size)), master=self)
            button._ntimage_alt = image_alt

        if _is_dark("background"):
            # For Checkbuttons, we need to set `image` and `selectimage` at
            # the same time. Otherwise, when updating the `image` option
            # (such as when changing DPI), if the old `selectimage` has
            # just been overwritten, Tk will throw an error.
            image_kwargs = {"image": image_alt}
        else:
            image_kwargs = {"image": image}
        # Checkbuttons may switch the background to `selectcolor` in the
        # checked state, so check separately which image it needs to use in
        # that state to still ensure enough contrast with the background.
        if isinstance(button, tk.Checkbutton) and button.cget("selectcolor") != "":
            if self._windowingsystem != "x11":
                selectcolor = "selectcolor"
            else:
                # On X11, selectcolor isn't used directly for indicator-less
                # buttons. See `::tk::CheckEnter` in the Tk button.tcl source
                # code for details.
                r1, g1, b1 = _get_color("selectcolor")
                r2, g2, b2 = _get_color("activebackground")
                selectcolor = ((r1 + r2) / 2, (g1 + g2) / 2, (b1 + b2) / 2)
            if _is_dark(selectcolor):
                image_kwargs["selectimage"] = image_alt
            else:
                image_kwargs["selectimage"] = image

        button.configure(**image_kwargs, height="18p", width="18p")
