import tkinter as tk
from functools import partial

import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import src.lib.render as Render
from src.lib.match_type import MatchType
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
        self.geometry("787x316")
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1), weight=1)

        self.canvas = None

        self.histogram()
        self.render_options()

        self.root.image_controller.selected_image_eh.add(self.on_image_change)

    def histogram(self):
        self.histogram_main_frame = tb.Frame(self, bootstyle="light")
        self.histogram_main_frame.grid(
            column=0, row=0, sticky=tk.NSEW, padx=10, pady=10
        )

        self.histogram_graph(self.histogram_main_frame)
        self.histogram_buttons(self.histogram_main_frame)

    def histogram_buttons(self, parent):
        self.percentile_buttons = {}
        for col, percentile in enumerate([*Render.PERCENTILES, "Custom"]):
            text = f"{percentile}%" if percentile != "Custom" else percentile
            self.percentile_buttons[percentile] = tb.Button(
                parent,
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

    def histogram_graph(self, parent):
        histogram = tb.Frame(parent, bootstyle="light")
        c = len(Render.PERCENTILES) + 1
        histogram.grid(
            column=0, columnspan=c, row=1, sticky=tk.NSEW, padx=10, pady=(10, 0)
        )

        if self.check_if_image_selected():
            image_selected = self.root.image_controller.get_selected_image()

            image_selected.update_histogram_lines()
            fig = image_selected.histogram

            if self.canvas is not None:
                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=histogram)
            self.canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.NSEW)
            self.canvas.draw()

            self.toolbar = NavigationToolbar2Tk(
                self.canvas, histogram, pack_toolbar=False
            )
            self.toolbar.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

            self.toolbar.update()

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
        self.histogram_graph(self.histogram_main_frame)
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

        self.histogram_graph(self.histogram_main_frame)
        self.root.update()

    def on_image_change(self, image):
        if image is None or image.file_type == "png":
            self.set_scaling(None)
            self.set_colour_map(None)
            self.set_percentile(None)
            self.set_vmin_vmax(None)
            self.update_percentile_buttons()
            self.set_grid_lines_box_state(None)
            return

        self.update_percentile_buttons()
        self.set_vmin_vmax(image)
        self.set_scaling(image.stretch)
        self.set_colour_map(image.colour_map)
        self.histogram_graph(self.histogram_main_frame)
        self.set_grid_lines_box_state(image.grid_lines)

        self.root.update()

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
