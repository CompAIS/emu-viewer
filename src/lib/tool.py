import os
import tkinter
import tkinter as tk
import tkinter.simpledialog
from tkinter import simpledialog, ttk

import matplotlib as mpl
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Very janky fix to get custom images to display, not sure how to edit matplotlib cbook images
ASSETS_FOLDER = "../../../../../../resources/assets/"
script_dir = os.path.dirname(__file__)
image_path = "resources/assets/"


def set_tooltip(widget, text):
    def show_tooltip(event):
        tooltip_label.config(text=text)
        tooltip_label.place(x=event.x_root + 10, y=event.y_root + 10)

    def hide_tooltip(event):
        tooltip_label.place_forget()

    tooltip_label = tk.Label(widget, text="", background="lightyellow", relief="solid")

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)


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

        # Used for menus that only accept strings
        self.line_colour_menu = tk.StringVar(value="red")
        self.line_size_menu = tk.StringVar(value="2")
        self.font_colour_menu = tk.StringVar(value="red")
        self.font_size_menu = tk.StringVar(value="12")
        self.tolerance_menu = tk.StringVar(value="1000")
        # Initial drawing variables
        self.line_colour = "red"
        self.line_size = 2
        self.font_colour = "red"
        self.font_size = 12
        # List tracker, used for deletion
        self.lines = []
        self.dots = []
        self.tolerance = 3000

        self.dragging = False
        self.selection_rect = None
        self.box_start = None
        self.box_end = None

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
                "Settings",
                "Annotation Settings",
                "subplots",
                "annotation_settings",
            ),
            (None, None, None, None),
            ("Save", "Save the figure", "filesave", "save_figure"),
            (None, None, None, None),
        )
        super().__init__(canvas, parent, pack_toolbar=pack)
        # Initialize button_press_callback and motion_notify_callback
        self.button_press_callback = None
        self.motion_notify_callback = None

        image_path = "resources/assets/"
        custom_button_frame = tk.Frame(self)
        custom_button_frame.pack(fill="x")

        # Line button
        line_image = tk.PhotoImage(file=f"{image_path}linetool.png")
        line_button = tk.Button(
            custom_button_frame,
            image=line_image,
            command=self.draw_line,
            width=25,
            height=25,
        )
        line_button.image = line_image  # Set the image for the button
        set_tooltip(line_button, "Draw line on figure")
        line_button.pack(side="left", padx=5, pady=5)

        # Type button
        type_image = tk.PhotoImage(file=f"{image_path}typetool.png")
        type_button = tk.Button(
            custom_button_frame,
            image=type_image,
            command=self.type_figure,
            width=25,
            height=25,
        )
        type_button.image = type_image
        set_tooltip(type_button, "Type on figure")
        type_button.pack(side="left", padx=5, pady=5)

        # Eraser button
        erase_image = tk.PhotoImage(file=f"{image_path}erasetool.png")
        erase_button = tk.Button(
            custom_button_frame,
            image=erase_image,
            command=self.erase_annotations,
            width=25,
            height=25,
        )
        erase_button.image = erase_image
        set_tooltip(erase_button, "Erase Annotations")
        erase_button.pack(side="left", padx=5, pady=5)

        # Clear button
        clear_image = tk.PhotoImage(file=f"{image_path}bintool.png")
        clear_button = tk.Button(
            custom_button_frame,
            image=clear_image,
            command=self.clear_all,
            width=25,
            height=25,
        )
        clear_button.image = clear_image
        set_tooltip(clear_button, "Clear Annotations")
        clear_button.pack(side="left", padx=5, pady=5)

    def toggle_button(self):
        # Disconnect the event handlers, used to make sure clicks dont activate multiple functions
        if (
            hasattr(self, "button_press_callback")
            and self.button_press_callback is not None
        ):
            self.canvas.mpl_disconnect(self.button_press_callback)

        if (
            hasattr(self, "button_press_callback")
            and self.button_press_callback is not None
        ):
            self.canvas.mpl_disconnect(self.button_press_callback)

        if (
            hasattr(self, "motion_notify_callback")
            and self.motion_notify_callback is not None
        ):
            self.canvas.mpl_disconnect(self.motion_notify_callback)
        self.canvas.widgetlock.release(self)

    def erase_annotations(self):
        # Erase annotations by click or hold click
        # The sensitivity area is defined by tolerance
        # Similar to a paint tool's eraser circle, it is fixed no matter the zoom out or in
        self.toggle_button()
        self.set_message("Click or hold click to erase annotations on the canvas")
        if not self.canvas.widgetlock.available(self):
            self.set_message("erase tool unavailable")
            return
        if self.mode == "erase_tool":
            self.mode = ""
        elif self.mode != "erase_tool":
            self.canvas.widgetlock(self)
            self.mode = "erase_tool"

            def on_motion(event):
                if event.button == 1:
                    self.clear_on_motion(event)

            # Connect the event handlers for erasing only when the left mouse button is held down
            self.button_press_callback = self.canvas.mpl_connect(
                "button_press_event", self.clear_on_click
            )
            self.motion_notify_callback = self.canvas.mpl_connect(
                "motion_notify_event", on_motion
            )

    def clear_on_click(self, event):
        # Remove the clicked annotation (dots or text)
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes

            # Check for lines
            for line in ax.lines:
                xdata, ydata = line.get_data()
                for xline, yline in zip(xdata, ydata):
                    distance = (xline - x) ** 2 + (yline - y) ** 2
                    if distance < self.tolerance:
                        line.remove()

            # Check for text annotations
            for annotation in ax.texts:
                xdata, ydata = annotation.get_position()
                distance = (xdata - x) ** 2 + (ydata - y) ** 2
                if distance < self.tolerance:
                    annotation.remove()

            self.canvas.draw()

    def clear_on_motion(self, event):
        # Remove annotations (lines and text) while hovering over them
        if event.inaxes:
            x, y = event.xdata, event.ydata
            ax = event.inaxes

            # Check for lines
            for line in ax.lines:
                xdata, ydata = line.get_data()
                for xline, yline in zip(xdata, ydata):
                    distance = (xline - x) ** 2 + (yline - y) ** 2
                    if distance < self.tolerance:
                        line.remove()

            # Check for text annotations
            for annotation in ax.texts:
                xdata, ydata = annotation.get_position()
                distance = (xdata - x) ** 2 + (ydata - y) ** 2
                if distance < self.tolerance:
                    annotation.remove()

            self.canvas.draw()

    def draw_line(self):
        # Styled similar to aladin's draw, dots are created and lines are created between dots
        self.toggle_button()
        self.set_message(
            "Click or hold click to draw dots connected by lines on the canvas"
        )
        if not self.canvas.widgetlock.available(self):
            self.set_message("line tool unavailable")
            return
        if self.mode == "line_tool":
            self.mode = ""
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
            self.dots.append(red_dot[0])  # Add the dot to the list of dots

            if len(self.clicked_points) > 1:
                x0, y0 = self.clicked_points[-2]
                x1, y1 = self.clicked_points[-1]

                # Create a line and add it to the list of lines
                line = ax.plot(
                    [x0, x1], [y0, y1], color=self.line_colour, linewidth=self.line_size
                )
                self.lines.append(line[0])  # Add the line to the list of lines
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
        # Disconnects itself after a single use
        if self.mode == "type_tool":
            # If the "Type" tool is already active, deactivate it
            self.deactivate_type_tool()
        else:
            # Activate the "Type" tool
            self.canvas.widgetlock(self)
            self.mode = "type_tool"
            self.set_message("Click on the figure to place text")

            # Connect a new event handler for the button press event
            self.button_press_callback = self.canvas.mpl_connect(
                "button_press_event", self.on_click
            )

    def deactivate_type_tool(self):
        # Deactivate the "Type" tool
        self.canvas.widgetlock.release(self)
        self.mode = ""
        self.set_message("")

        # Disconnect the event handler
        if self.button_press_callback is not None:
            self.canvas.mpl_disconnect(self.button_press_callback)
            self.button_press_callback = None

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
        # Clear annotations button, creates a popup to allow the user to select
        # lines, text, or all
        input_window = tk.Toplevel(self)
        input_window.title("Clear Annotations")
        input_window.geometry("125x155")

        frame = tk.Frame(input_window)
        frame.grid(row=0, column=0, padx=10, pady=10)

        button_clear_lines = tk.Button(
            frame,
            text="Clear Lines",
            command=lambda: self.clear_annotations(clear_lines=True, clear_text=False),
            width=12,  # Set all buttons to same width
        )
        button_clear_text = tk.Button(
            frame,
            text="Clear Text",
            command=lambda: self.clear_annotations(clear_lines=False, clear_text=True),
            width=12,
        )
        button_clear_all = tk.Button(
            frame,
            text="Clear All",
            command=lambda: self.clear_annotations(clear_lines=True, clear_text=True),
            width=12,
        )

        # Grid layout for buttons
        button_clear_lines.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        button_clear_text.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        button_clear_all.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        button_close = tb.Button(
            frame,
            bootstyle="danger-outline",
            text="Close",
            command=input_window.destroy,
        )
        button_close.grid(row=4, column=0, pady=10, padx=10, columnspan=2)

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
        input_window.geometry("250x400")

        for i in range(2):
            input_window.grid_columnconfigure(i, weight=1)

        for i in range(5):
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

        size_options = [2, 4, 6, 8, 12, 16]
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
        text_size_options = [12, 4, 8, 16, 24]
        text_size_menu = ttk.Combobox(
            input_window,
            textvariable=self.font_size_menu,
            values=text_size_options,
            state="readonly",
        )
        text_size_menu.grid(row=3, column=1, padx=10, pady=10)

        eraser_size_label = tk.Label(input_window, text="Eraser Size")
        eraser_size_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        eraser_size_options = [1000, 200, 600, 1500, 2000, 3000]
        eraser_size_menu = ttk.Combobox(
            input_window,
            textvariable=self.tolerance_menu,
            values=eraser_size_options,
            state="readonly",
        )
        eraser_size_menu.grid(row=4, column=1, padx=10, pady=10)

        apply_all_button = tb.Button(
            input_window,
            bootstyle="success",
            text="Apply All",
            command=lambda: self.apply_all(input_window),
        )
        apply_all_button.grid(row=5, column=1, padx=10, pady=10)

        cancel_button = tb.Button(
            input_window,
            text="Close",
            bootstyle="danger-outline",
            command=input_window.destroy,
        )
        cancel_button.grid(row=5, column=0, padx=10, pady=10)

    def apply_all(self, input_window):
        # This function is called when the "Apply All" button is clicked
        self.line_colour = self.line_colour_menu.get()
        self.line_size = self.line_size_menu.get()
        self.font_colour = self.font_colour_menu.get()
        self.font_size = self.font_size_menu.get()
        self.tolerance = int(self.tolerance_menu.get())
        print(self.tolerance)
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
