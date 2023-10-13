import os
import tkinter
import tkinter as tk
import tkinter.simpledialog
from tkinter import simpledialog, ttk

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Very janky fix to get custom images to display, not sure how to edit matplotlib cbook images
ASSETS_FOLDER = "../../../../../../resources/assets/"


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
        self.line_colour_menu = tk.StringVar(value="red")
        self.line_size_menu = tk.StringVar(value="2")
        self.font_colour_menu = tk.StringVar(value="red")
        self.font_size_menu = tk.StringVar(value="12")

        self.line_colour = "red"
        self.line_size = "2"
        self.font_colour = "red"
        self.font_size = "12"

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
                f"{ASSETS_FOLDER}/line",
                "draw_line",
            ),
            (None, None, None, None),
            (
                "Type",
                "Type on the figure",
                f"{ASSETS_FOLDER}/type",
                "type_figure",
            ),
            (None, None, None, None),
            # (
            #     "Erase",
            #     "Erase  annotations on figure",
            #     f"{ASSETS_FOLDER}/bin",
            #     "erase_annotations",
            # ),
            # (None, None, None, None),
            (
                "Clear",
                "Clear all annotations on figure",
                f"{ASSETS_FOLDER}/bin",
                "clear_all",
            ),
            (None, None, None, None),
            (
                "Settings",
                "Annotation Settings",
                f"{ASSETS_FOLDER}/settings",
                "annotation_settings",
            ),
            (None, None, None, None),
            ("Save", "Save the figure", "filesave", "save_figure"),
        )
        super().__init__(canvas, parent, pack_toolbar=pack)
        # Initialize button_press_callback and motion_notify_callback
        self.button_press_callback = None
        self.motion_notify_callback = None

    # def erase_annotations(self):
    #     # Disconnect the event handlers for the "Type" tool
    #     if hasattr(self, "button_press_callback") and self.button_press_callback is not None:
    #         self.canvas.mpl_disconnect(self.button_press_callback)

    #     # Disconnect the event handlers for the "Line" tool
    #     if hasattr(self, "motion_notify_callback") and self.motion_notify_callback is not None:
    #         self.canvas.mpl_disconnect(self.motion_notify_callback)

    #     # Connect the event handlers for erasing
    #     self.canvas.mpl_connect("button_press_event", self.on_click_to_erase)
    #     self.canvas.mpl_connect("motion_notify_event", self.on_drag_to_erase)

    # def on_click_to_erase(self, event):
    #     print("on click erase active")

    # def on_drag_to_erase(self, event):
    #     print("on click drag erase active")

    def draw_line(self):
        # Disconnect the event handlers for the "Type" tool
        if hasattr(self, "button_press_callback"):
            self.canvas.mpl_disconnect(self.button_press_callback)

        self.canvas.mpl_disconnect(
            self.button_press_callback
        )  # Make sure text button isn't active
        if not self.canvas.widgetlock.available(self):
            self.set_message("line tool unavailable")
            return
        if self.mode == "line_tool":
            self.mode = ""
            self.canvas.widgetlock.release(self)
        elif self.mode != "line_tool":
            self.canvas.widgetlock(self)
            self.mode = "line_tool"
            self.button_press_callback = self.canvas.mpl_connect(
                "button_press_event", self.on_left_click
            )
            self.motion_notify_callback = self.canvas.mpl_connect(
                "motion_notify_event", self.on_motion_notify
            )
        self.clicked_points = []

    def on_left_click(self, event):
        if self.mode == "line_tool" and event.inaxes and event.button == 1:
            x, y = event.xdata, event.ydata
            ax = event.inaxes

            self.clicked_points.append((x, y))

            red_dot = ax.plot(
                x, y, marker="o", markersize=self.line_size, color=self.line_colour
            )
            red_dot[0].set_markerfacecolor(self.line_colour)

            if len(self.clicked_points) > 1:
                # Connect the last two points with a line
                x0, y0 = self.clicked_points[-2]
                x1, y1 = self.clicked_points[-1]
                ax.plot(
                    [x0, x1], [y0, y1], color=self.line_colour, linewidth=self.line_size
                )

            self.canvas.draw()

    def on_motion_notify(self, event):
        if self.mode == "line_tool" and event.inaxes and event.button == 1:
            x, y = event.xdata, event.ydata
            ax = event.inaxes

            self.clicked_points.append((x, y))

            red_dot = ax.plot(
                x, y, marker="o", markersize=self.line_size, color=self.line_colour
            )
            red_dot[0].set_markerfacecolor(self.line_colour)

            if len(self.clicked_points) > 1:
                x0, y0 = self.clicked_points[-2]
                x1, y1 = self.clicked_points[-1]

                # Line with colour and size adjustables
                ax.plot(
                    [x0, x1], [y0, y1], color=self.line_colour, linewidth=self.line_size
                )
            self.canvas.draw()

    def type_figure(self):
        # Disconnect the event handlers for the "Line" tool
        if hasattr(self, "button_press_callback"):
            self.canvas.mpl_disconnect(self.button_press_callback)
        if hasattr(self, "motion_notify_callback"):
            self.canvas.mpl_disconnect(self.motion_notify_callback)

        # Activate the "Type" tool
        self.canvas.widgetlock(self)
        self.mode = "type_tool"
        self.set_message("Click on the figure to place text")

        # Connect a new event handler for the button press event
        self.button_press_callback = self.canvas.mpl_connect(
            "button_press_event", self.on_click
        )

    def on_click(self, event):
        # On click event for the typing button
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes

            # Prompt the user to enter text
            text = simpledialog.askstring("Type on Figure", "Enter text:")

            if text:
                ax.text(x, y, text, fontsize=self.font_size, color=self.font_colour)
                self.canvas.draw()
                self.set_message("")

            if self.button_press_callback is not None:
                # Disconnect the event handler
                self.canvas.mpl_disconnect(self.button_press_callback)
                self.button_press_callback = None

    def clear_all(self):
        # Clear annotations button, creates a popup to allow user to select
        # lines, text or all
        input_window = tk.Toplevel(self)
        input_window.title("Clear Annotations")
        input_window.geometry("250x125")

        frame = tk.Frame(input_window)
        frame.pack(pady=10)

        button_clear_lines = tk.Button(
            frame,
            text="Clear Lines",
            command=lambda: self.clear_annotations(clear_lines=True, clear_text=False),
        )
        button_clear_text = tk.Button(
            frame,
            text="Clear Text",
            command=lambda: self.clear_annotations(clear_lines=False, clear_text=True),
        )
        button_clear_both = tk.Button(
            input_window,
            text="Clear All ",
            command=lambda: self.clear_annotations(clear_lines=True, clear_text=True),
        )

        button_clear_lines.pack(side="left", padx=10)
        button_clear_text.pack(side="left", padx=10)

        # Button isnt red, needs work
        button_close = tk.Button(
            input_window,
            text="Close",
            command=input_window.destroy,
        )
        button_clear_both.pack(pady=10)
        button_close.pack(pady=10)

    def clear_annotations(self, clear_lines=False, clear_text=False):
        for ax in self.canvas.figure.get_axes():
            if clear_text:
                for annotation in ax.texts:
                    annotation.remove()

            if clear_lines:
                for line in ax.lines:
                    line.remove()

        self.canvas.draw()

    def annotation_settings(self):
        input_window = tk.Toplevel()
        input_window.title("Annotation Settings")
        input_window.geometry("300x300")

        for i in range(2):
            input_window.grid_columnconfigure(i, weight=1)

        for i in range(4):
            input_window.grid_rowconfigure(i, weight=1)

        line_color_label = tk.Label(input_window, text="Line Colour")
        line_color_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        color_options = ["red", "blue", "green", "white", "black"]
        line_colour_menu = ttk.Combobox(
            input_window,
            textvariable=self.line_colour_menu,
            values=color_options,
            state="readonly",
        )
        line_colour_menu.grid(row=0, column=1, padx=10, pady=10)

        line_text_label = tk.Label(input_window, text="Line Size")
        line_text_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        size_options = ["2", "4", "6", "8", "12"]
        line_size_menu = ttk.Combobox(
            input_window,
            textvariable=self.line_size_menu,
            values=size_options,
            state="readonly",
        )
        line_size_menu.grid(row=1, column=1, padx=10, pady=10)

        text_colour_label = tk.Label(input_window, text="Text Colour")
        text_colour_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        text_color_options = ["red", "blue", "green", "white", "black"]
        text_color_menu = ttk.Combobox(
            input_window,
            textvariable=self.font_colour_menu,
            values=text_color_options,
            state="readonly",
        )
        text_color_menu.grid(row=2, column=1, padx=10, pady=10)

        text_size_label = tk.Label(input_window, text="Text Size")
        text_size_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        text_size_options = ["12", "4", "8", "16", "24"]
        text_size_menu = ttk.Combobox(
            input_window,
            textvariable=self.font_size_menu,
            values=text_size_options,
            state="readonly",
        )
        text_size_menu.grid(row=3, column=1, padx=10, pady=10)

        apply_all_button = tk.Button(
            input_window, text="Apply All", command=lambda: self.apply_all(input_window)
        )
        apply_all_button.grid(row=4, column=1, padx=10, pady=10)

        cancel_button = tk.Button(
            input_window,
            text="Close",
            command=input_window.destroy,
            bg="red",
            fg="white",
        )
        cancel_button.grid(row=4, column=0, padx=10, pady=10)

    def apply_all(self, input_window):
        # This function is called when the "Apply All" button is clicked
        self.line_colour = self.line_colour_menu.get()
        self.line_size = self.line_size_menu.get()
        self.font_colour = self.font_colour_menu.get()
        self.font_size = self.font_size_menu.get()
        input_window.destroy()

    def save_figure(self, *args):
        """
        Mostly stolen from base class. Modified to fit our needs.
        """

        filetypes = self.canvas.get_supported_filetypes().copy()
        default_filetype = self.canvas.get_default_filetype()

        default_filetype_name = filetypes.pop(default_filetype)
        sorted_filetypes = [(default_filetype, default_filetype_name)] + sorted(
            filetypes.items()
        )
        tk_filetypes = [(name, "*.%s" % ext) for ext, name in sorted_filetypes]

        defaultextension = ""
        initialdir = os.path.expanduser(mpl.rcParams["savefig.directory"])
        initialfile = self.canvas.get_default_filename()
        fname = tkinter.filedialog.asksaveasfilename(
            master=self.canvas.get_tk_widget().master,
            title="Save the figure",
            filetypes=tk_filetypes,
            defaultextension=defaultextension,
            initialdir=initialdir,
            initialfile=initialfile,
        )

        if fname in ["", ()]:
            return
        if initialdir != "":
            mpl.rcParams["savefig.directory"] = os.path.dirname(str(fname))
        try:
            # Where our implementation changes things https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
            fig = self.canvas.figure
            extent = (
                fig.axes[0]
                .get_window_extent()
                .transformed(fig.dpi_scale_trans.inverted())
            )
            print(extent)
            fig.savefig(fname, bbox_inches=extent)
        except Exception as e:
            tkinter.messagebox.showerror("Error saving file", str(e))

    @staticmethod
    def _mouse_event_to_message(event):
        """
        Stolen from base class. The base class was attaching some extra text to our tooltip.
        We don't want that, so I've forcibly removed it here.
        """

        if event.inaxes and event.inaxes.get_navigate():
            try:
                s = event.inaxes.format_coord(event.xdata, event.ydata)
            except (ValueError, OverflowError) as e:
                print(e)
            else:
                return s.rstrip()
        return ""
