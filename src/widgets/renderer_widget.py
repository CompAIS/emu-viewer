import sys
import tkinter as tk
import weakref
from functools import partial

import ttkbootstrap as tb
from matplotlib.backend_bases import CloseEvent
from matplotlib.backends import _backend_tk
from matplotlib.backends._backend_tk import FigureCanvasTk
from matplotlib.backends.backend_agg import FigureCanvasAgg

import src.lib.render as Render
from src.lib.match_type import MatchType
from src.lib.tool import HistoToolbar
from src.widgets.base_widget import BaseWidget

scaling_options = [
    "Linear",
    "Log",
    "Sqrt",
]

colour_map_options = [
    "viridis",
    "plasma",
    "inferno",
    "magma",
    "cividis",
    "Greys",
    "Purples",
    "Blues",
    "Greens",
    "Oranges",
    "Reds",
    "binary",
    "hot",
]

NO_IMAGE_OPEN = "No image open"


class RendererWidget(BaseWidget):
    label = "Renderer Configuration"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)

        self.canvas = self.toolbar = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.render_options()
        self.create_histogram()

        self.root.image_controller.selected_image_eh.add(self.on_image_change)
        self.on_image_change(self.root.image_controller.get_selected_image())

    def create_histogram(self):
        self.histogram_main_frame = tb.Frame(self, bootstyle="light")
        self.histogram_main_frame.grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )
        self.histogram_main_frame.grid_rowconfigure(0, weight=0)
        self.histogram_main_frame.grid_rowconfigure(1, weight=1)

        self.histogram_buttons()
        self.root.update()
        self.histogram_graph()

    def histogram_buttons(self):
        self.percentile_buttons = {}
        for col, percentile in enumerate([*Render.PERCENTILES, "Custom"]):
            text = f"{percentile}%" if percentile != "Custom" else percentile
            self.histogram_main_frame.grid_columnconfigure(col, weight=0)
            self.percentile_buttons[percentile] = tb.Button(
                self.histogram_main_frame,
                text=text,
                bootstyle="dark",
                command=partial(self.set_percentile, str(percentile)),
            )
            self.percentile_buttons[percentile].grid(
                column=col, row=0, sticky=tk.NSEW, padx=10, pady=10
            )

        self.update_percentile_buttons()

    def update_percentile_buttons(self):
        for percentile, button in self.percentile_buttons.items():
            button.configure(bootstyle="dark")

            if self.check_if_image_selected() and (
                str(percentile)
                == self.root.image_controller.get_selected_image().selected_percentile
            ):
                button.configure(bootstyle="medium")

    def histogram_graph(self):
        self.histogram_frame = tb.Frame(self.histogram_main_frame, bootstyle="light")
        self.histogram_frame.grid_rowconfigure(0, weight=1)
        self.histogram_frame.grid_columnconfigure(0, weight=1)

        self.histo_fig = Render.create_histogram_graph()
        self.canvas = HistogramCanvasTkAgg(self.histo_fig, master=self.histogram_frame)
        self.canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.NSEW)
        self.canvas.mpl_connect("button_press_event", self.on_histo_click)
        self.canvas.draw()

        self.toolbar = HistoToolbar(self.canvas, self.histogram_frame, pack=False)
        self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.toolbar.update()

        self.root.update()

        self.histo_fig.set_size_inches(
            *Render.get_size_inches(self.canvas.get_tk_widget())
        )

    def update_histogram_graph(self):
        if not self.check_if_image_selected():
            self.histogram_frame.grid_forget()
            return

        c = len(Render.PERCENTILES) + 1
        self.histogram_frame.grid(
            column=0, columnspan=c, row=1, sticky=tk.NSEW, padx=10, pady=(10, 0)
        )

        image_selected = self.root.image_controller.get_selected_image()

        self.histo_fig = Render.draw_histogram_graph(
            self.histo_fig,
            image_selected.histo_counts,
            image_selected.histo_bins,
            image_selected.vmin,
            image_selected.vmax,
        )
        self.canvas.draw()

    def update_histogram_lines(self):
        if not self.check_if_image_selected():
            return

        image_selected = self.root.image_controller.get_selected_image()

        self.histo_fig = Render.draw_histogram_lines(
            self.histo_fig,
            image_selected.vmin,
            image_selected.vmax,
        )
        self.canvas.draw()

    def render_options(self):
        render = tb.Frame(self, width=100, bootstyle="light")
        render.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tb.Label(render, text="Render Options", bootstyle="inverse-light")
        label.grid(column=0, columnspan=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.min_entry = self.custom_options(render, "Min", 0, 1)
        self.max_entry = self.custom_options(render, "Max", 0, 2)

        self.scaling_dropdown = self.dropdown_options(
            render,
            "Scaling",
            scaling_options,
            self.on_select_scaling,
            0,
            3,
        )
        self.colour_map_dropdown = self.dropdown_options(
            render,
            "Colour Map",
            colour_map_options,
            self.on_select_colour_map,
            0,
            4,
        )

        grid_lines_lbl = tb.Label(render, bootstyle="inverse-light", text="Grid Lines")
        grid_lines_lbl.grid(column=0, row=5, sticky=tk.NSEW, padx=10, pady=10)

        self.grid_lines_state = tk.BooleanVar()
        self.grid_lines_cbtn = tb.Checkbutton(
            render,
            bootstyle="primary-round-toggle",
            text=None,
            command=self.on_grid_lines,
            variable=self.grid_lines_state,
        )
        self.grid_lines_cbtn.grid(row=5, column=1, sticky=tk.W, padx=10, pady=10)
        self.set_grid_lines_box_state(None)

    def custom_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        entry = tb.Entry(parent, bootstyle="dark")
        entry.bind("<FocusOut>", self.on_entry_focusout)
        entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        entry.configure(state="disabled")

        return entry

    def dropdown_options(self, parent, text, options, func, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text=NO_IMAGE_OPEN, bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in options:
            dropdown_menu.add_command(label=option, command=partial(func, option))

        dropdown["menu"] = dropdown_menu

        return dropdown

    # These four functions update state of the UI with the new elements,
    #   and will update the image data, but will not re-render the image
    def set_scaling(self, option):
        if option is None:
            self.scaling_dropdown["text"] = NO_IMAGE_OPEN
            return

        self.scaling_dropdown["text"] = option

        if not self.check_if_image_selected():
            return

        self.root.image_controller.get_selected_image().set_scaling(option)

    def set_colour_map(self, option):
        if option is None:
            self.colour_map_dropdown["text"] = NO_IMAGE_OPEN
            return

        self.colour_map_dropdown["text"] = option

        if not self.check_if_image_selected():
            return

        self.root.image_controller.get_selected_image().set_colour_map(option)

    def set_vmin_vmax(self, image):
        # Update entries with new percentiles, from cached
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)

        if image is not None:
            self.min_entry.configure(state="enabled")
            self.max_entry.configure(state="enabled")
            self.min_entry.insert(0, str(image.vmin))
            self.max_entry.insert(0, str(image.vmax))
        else:
            self.min_entry.configure(state="disabled")
            self.max_entry.configure(state="disabled")

    def set_percentile(self, percentile):
        if not self.check_if_image_selected():
            return

        if percentile is None:
            self.set_vmin_vmax(None)
            self.update_percentile_buttons()
            return

        selected_image = self.root.image_controller.get_selected_image()
        selected_image.set_selected_percentile(percentile)
        self.update_percentile_buttons()
        self.set_vmin_vmax(selected_image)
        self.update_histogram_lines()
        self.root.image_controller.get_selected_image().update_norm()

        self.update_matched_images()

    def set_grid_lines_box_state(self, state):
        """
        Set the state of the checkbox to the given state.
        """

        if state is None:
            self.grid_lines_state.set(False)
            self.grid_lines_cbtn.configure(state="disabled")
        else:
            self.grid_lines_cbtn.configure(state="enabled")
            self.grid_lines_state.set(state)

    def on_grid_lines(self):
        image = self.root.image_controller.get_selected_image()
        if image is None:
            self.set_grid_lines_box_state(None)
            return

        state = image.toggle_grid_lines()
        self.set_grid_lines_box_state(state)

    # These functions listen to events and behave accordingly
    def on_select_scaling(self, option):
        if not self.check_if_image_selected():
            return

        self.set_scaling(option)
        self.root.image_controller.get_selected_image().update_norm()

        self.update_matched_images()

        self.root.update()

    def on_select_colour_map(self, option):
        if not self.check_if_image_selected():
            return

        self.set_colour_map(option)
        self.root.image_controller.get_selected_image().update_colour_map()

        self.update_matched_images()

        self.root.update()

    def on_entry_focusout(self, event):
        if not self.check_if_image_selected():
            return

        vmin = float(self.min_entry.get())
        vmax = float(self.max_entry.get())
        self.root.image_controller.get_selected_image().set_vmin_vmax_custom(vmin, vmax)
        self.update_percentile_buttons()
        self.root.image_controller.get_selected_image().update_norm()
        self.update_matched_images()
        self.update_histogram_lines()
        self.root.update()

    def on_image_change(self, image):
        if image is None or image.file_type == "png":
            self.set_scaling(None)
            self.set_colour_map(None)
            self.set_percentile(None)
            self.set_vmin_vmax(None)
            self.update_percentile_buttons()
            self.update_histogram_graph()
            self.set_grid_lines_box_state(None)
            return

        self.update_percentile_buttons()
        self.set_vmin_vmax(image)
        self.set_scaling(image.stretch)
        self.set_colour_map(image.colour_map)
        self.update_histogram_graph()
        self.set_grid_lines_box_state(image.grid_lines)

        self.root.update()

    def on_histo_click(self, event):
        if self.histo_fig.canvas.toolbar.mode != "":
            return

        # this is a matplotlib event, so we don't have the access to the x/y for the context menu position
        # (the pointer)
        # so grab it manually
        window_x, window_y = (
            self.canvas.get_tk_widget().winfo_pointerx(),
            self.canvas.get_tk_widget().winfo_pointery(),
        )

        ax = self.histo_fig.axes[0]
        if ax == event.inaxes and event.button == 3:
            # transform from position on the canvas to image position
            image_x, _ = ax.transData.inverted().transform((event.x, event.y))
            self.show_context_menu(event, image_x, window_x, window_y)

    def show_context_menu(self, event, image_x, window_x, window_y):
        self.context_menu = HistogramContextMenu(self, self.histo_fig, image_x)
        self.context_menu.post(window_x, window_y)

    def check_if_image_selected(self):
        image = self.root.image_controller.get_selected_image()
        return image is not None and image.file_type != "png"

    def update_matched_images(self):
        for image in self.root.image_controller.get_images_matched_to(MatchType.RENDER):
            if image == self.root.image_controller.get_selected_image():
                continue

            image.match_render(self.root.image_controller.get_selected_image())

    def close(self):
        self.root.image_controller.selected_image_eh.remove(self.on_image_change)

        super().close()


class HistogramContextMenu(tk.Menu):
    def __init__(self, render_widget, histogram, xdata):
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
        self.render_widget.clipboard_clear()
        self.render_widget.clipboard_append(text)
        self.render_widget.update()


# overriding internals again because YAY matplotlib!!!
# (don't tell anybody this but I'm actually ANGRY!)
class HistrogramFigureCanvasTk(FigureCanvasTk):
    def __init__(self, figure=None, master=None):
        super().__init__(figure)
        self._idle_draw_id = None
        self._event_loop_id = None
        w, h = self.get_width_height(physical=True)
        self._tkcanvas = tk.Canvas(
            master=master,
            background="white",
            width=w,
            height=h,
            borderwidth=0,
            highlightthickness=0,
        )
        self._tkphoto = tk.PhotoImage(master=self._tkcanvas, width=w, height=h)
        self._tkcanvas.create_image(w // 2, h // 2, image=self._tkphoto)
        self._tkcanvas.bind("<Configure>", self.resize)
        if sys.platform == "win32":
            self._tkcanvas.bind("<Map>", self._update_device_pixel_ratio)
        self._tkcanvas.bind("<Key>", self.key_press)
        self._tkcanvas.bind("<Motion>", self.motion_notify_event)
        self._tkcanvas.bind("<Enter>", self.enter_notify_event)
        self._tkcanvas.bind("<Leave>", self.leave_notify_event)
        self._tkcanvas.bind("<KeyRelease>", self.key_release)
        for name in ["<Button-1>", "<Button-2>", "<Button-3>"]:
            self._tkcanvas.bind(name, self.button_press_event)
        for name in ["<Double-Button-1>", "<Double-Button-2>", "<Double-Button-3>"]:
            self._tkcanvas.bind(name, self.button_dblclick_event)
        for name in ["<ButtonRelease-1>", "<ButtonRelease-2>", "<ButtonRelease-3>"]:
            self._tkcanvas.bind(name, self.button_release_event)

        # Mouse wheel on Linux generates button 4/5 events
        for name in "<Button-4>", "<Button-5>":
            self._tkcanvas.bind(name, self.scroll_event)
        # Mouse wheel for windows goes to the window with the focus.
        # Since the canvas won't usually have the focus, bind the
        # event to the window containing the canvas instead.
        # See https://wiki.tcl-lang.org/3893 (mousewheel) for details
        root = self._tkcanvas.winfo_toplevel()

        # Prevent long-lived references via tkinter callback structure GH-24820
        weakself = weakref.ref(self)
        weakroot = weakref.ref(root)

        def scroll_event_windows(event):
            self = weakself()
            if self is None:
                root = weakroot()
                if root is not None:
                    root.unbind("<MouseWheel>", scroll_event_windows_id)
                return
            return self.scroll_event_windows(event)

        scroll_event_windows_id = root.bind("<MouseWheel>", scroll_event_windows, "+")

        # Can't get destroy events by binding to _tkcanvas. Therefore, bind
        # to the window and filter.
        def filter_destroy(event):
            self = weakself()
            if self is None:
                root = weakroot()
                if root is not None:
                    root.unbind("<Destroy>", filter_destroy_id)
                return
            if event.widget is self._tkcanvas:
                CloseEvent("close_event", self)._process()

        filter_destroy_id = root.bind("<Destroy>", filter_destroy, "+")

        # THIS IS THE THING WE CHANGED
        # COMMENTING OUT A SINGLE LINE
        # self._tkcanvas.focus_set()

        self._rubberband_rect_black = None
        self._rubberband_rect_white = None


class HistogramCanvasTkAgg(FigureCanvasAgg, HistrogramFigureCanvasTk):
    def draw(self):
        super().draw()
        self.blit()

    def blit(self, bbox=None):
        _backend_tk.blit(
            self._tkphoto, self.renderer.buffer_rgba(), (0, 1, 2, 3), bbox=bbox
        )
