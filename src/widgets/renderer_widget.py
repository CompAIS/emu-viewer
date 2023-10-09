import tkinter as tk
from functools import partial

import ttkbootstrap as tb

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


class RendererWidget(BaseWidget):
    label = "Renderer Configuration"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)
        self.selected_image = self.root.image_controller.get_selected_image()

        if self.selected_image is None:
            self.selected_scaling_option = scaling_options[0]
            self.selected_colour_map_option = colour_map_options[0]
        else:
            self.selected_scaling_option = self.selected_image.stretch
            self.selected_colour_map_option = self.selected_image.colour_map

        self.histogram()
        self.render_options()

        self.root.image_controller.selected_image_eh.add(self.update_render_values)

    def histogram(self):
        frame = tb.Frame(self, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.histogram_graph(frame)
        self.histogram_buttons(frame)

    def histogram_buttons(self, parent):
        button_90 = tb.Button(
            parent,
            text="90%",
            bootstyle="dark",
            command=partial(self.set_selected_image_histogram_scaling, 0.5, 90),
        )
        button_90.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_95 = tb.Button(
            parent,
            text="95%",
            bootstyle="dark",
            command=partial(self.set_selected_image_histogram_scaling, 0.5, 95),
        )
        button_95.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_99 = tb.Button(
            parent,
            text="99%",
            bootstyle="dark",
            command=partial(self.set_selected_image_histogram_scaling, 0.5, 99),
        )
        button_99.grid(column=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_995 = tb.Button(
            parent,
            text="99.5%",
            bootstyle="dark",
            command=partial(self.set_selected_image_histogram_scaling, 0.5, 99.5),
        )
        button_995.grid(column=3, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_custom = tb.Button(
            parent,
            text="Custom",
            bootstyle="dark",
            command=self.set_selected_image_histogram_scaling_custom,
        )
        button_custom.grid(column=4, row=0, sticky=tk.NSEW, padx=10, pady=10)

    def set_selected_image_histogram_scaling_custom(self):
        if self.min_entry.get() == "" or self.max_entry.get() == "":
            return

        self.set_selected_image_histogram_scaling(
            float(self.min_entry.get()), float(self.max_entry.get())
        )

    def set_selected_image_histogram_scaling(self, vmin, vmax):
        self.selected_image = self.root.image_controller.get_selected_image()

        if self.check_if_image_selected():
            self.selected_image.vmin = vmin
            self.selected_image.vmax = vmax
            self.selected_image.update_norm()
            self.root.update()

    def histogram_graph(self, parent):
        histogram = tb.Frame(parent, bootstyle="dark")
        histogram.grid(column=0, columnspan=5, row=1, sticky=tk.NSEW, padx=10, pady=10)

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
            self.selected_scaling_option,
            self.select_scaling_option,
            0,
            3,
        )
        self.colour_map_dropdown = self.dropdown_options(
            render,
            "Colour Map",
            colour_map_options,
            self.selected_colour_map_option,
            self.select_colour_map_option,
            0,
            4,
        )

    def custom_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        entry = tb.Entry(parent, bootstyle="dark")
        entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        return entry

    def dropdown_options(
        self, parent, text, options, selected_option, func, gridX, gridY
    ):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        dropdown = tb.Menubutton(parent, text=selected_option, bootstyle="dark")
        dropdown.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        dropdown_menu = tk.Menu(dropdown, tearoff=0)

        for option in options:
            dropdown_menu.add_command(
                label=option,
                command=partial(func, option, dropdown),
            )

        dropdown["menu"] = dropdown_menu

        return dropdown

    def select_scaling_option(self, option, menu_button):
        self.selected_scaling_option = option
        menu_button["text"] = option

        self.selected_image = self.root.image_controller.get_selected_image()

        if self.check_if_image_selected():
            self.selected_image.stretch = self.selected_scaling_option
            self.selected_image.update_norm()
            self.root.update()

    def select_colour_map_option(self, option, menu_button):
        self.selected_colour_map_option = option
        menu_button["text"] = option

        self.selected_image = self.root.image_controller.get_selected_image()

        if self.check_if_image_selected():
            self.selected_image.colour_map = self.selected_colour_map_option
            self.selected_image.update_colour_map()
            self.root.update()

    def update_render_values(self, image):
        if image is None:
            self.selected_scaling_option = scaling_options[0]
            self.selected_colour_map_option = colour_map_options[0]
        else:
            self.update_selected_scaling(image.stretch)
            self.update_selected_colour_map(image.colour_map)

        self.root.update()

    def update_selected_scaling(self, option):
        self.selected_scaling_option = option
        self.scaling_dropdown["text"] = option

    def update_selected_colour_map(self, option):
        self.selected_colour_map_option = option
        self.colour_map_dropdown["text"] = option

    def check_if_image_selected(self):
        if self.root.image_controller.get_selected_image() is None:
            return False

        return True

    def close(self):
        self.root.image_controller.selected_image_eh.remove(self.update_render_values)

        super().close()
