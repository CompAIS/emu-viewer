import tkinter as tk
from functools import partial

import ttkbootstrap as tb

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


class RendererWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Render Configuration")
        self.resizable(0, 0)
        self.root = root

        self.grid_rowconfigure(0, weight=2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0)

        self.selected_image = self.root.image_controller.get_selected_image()

        if self.selected_image is None:
            self.selected_scaling_option = scaling_options[0]
            self.selected_colour_map_option = colour_map_options[0]
        else:
            self.selected_scaling_option = scaling_options[0]
            self.selected_colour_map_option = self.selected_image.colour_map

        self.histogram()
        self.render_options()

        self.protocol(
            "WM_DELETE_WINDOW", self.root.widget_controller.close_render_widget
        )

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
            self.selected_image.update_render = True
            self.selected_image.update_canvas()
            self.root.update()

    def histogram_graph(self, parent):
        histogram = tb.Frame(parent, bootstyle="dark")
        histogram.grid(column=0, columnspan=5, row=1, sticky=tk.NSEW, padx=10, pady=10)

    def render_options(self):
        render = tb.Frame(self, width=100, bootstyle="light")
        render.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tb.Label(render, text="Render Options", bootstyle="inverse-light")
        label.grid(column=0, columnspan=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.custom_options(render, "Min", 0, 1)

        self.custom_options(render, "Max", 0, 2)

        self.dropdown_options(render, "Scaling", self.selected_scaling_option, 0, 3)

        self.dropdown_options(
            render, "Colour Map", self.selected_colour_map_option, 0, 4
        )

    def custom_options(self, parent, text, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        if text == "Min":
            self.min_entry = tb.Entry(parent, bootstyle="dark")
            self.min_entry.grid(
                column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
            )
        elif text == "Max":
            self.max_entry = tb.Entry(parent, bootstyle="dark")
            self.max_entry.grid(
                column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
            )

    def dropdown_options(self, parent, text, selected_option, gridX, gridY):
        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        if text == "Scaling":
            self.scaling_dropdown = tb.Menubutton(
                parent, text=selected_option, bootstyle="dark"
            )
            self.scaling_dropdown.grid(
                column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
            )

            dropdown_menu = tk.Menu(self.scaling_dropdown, tearoff=0)

            for option in scaling_options:
                dropdown_menu.add_command(
                    label=option,
                    command=partial(
                        self.select_scaling_option, option, self.scaling_dropdown
                    ),
                )

            self.scaling_dropdown["menu"] = dropdown_menu
        elif text == "Colour Map":
            self.colour_map_dropdown = tb.Menubutton(
                parent, text=selected_option, bootstyle="dark"
            )
            self.colour_map_dropdown.grid(
                column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
            )

            dropdown_menu = tk.Menu(self.colour_map_dropdown, tearoff=0)

            for option in colour_map_options:
                dropdown_menu.add_command(
                    label=option,
                    command=partial(
                        self.select_colour_map_option, option, self.colour_map_dropdown
                    ),
                )

            self.colour_map_dropdown["menu"] = dropdown_menu

    def select_scaling_option(self, option, menu_button):
        self.selected_scaling_option = option
        menu_button["text"] = option

        self.selected_image = self.root.image_controller.get_selected_image()

        if self.check_if_image_selected():
            self.selected_image.stretch = self.selected_scaling_option
            self.selected_image.update_image_render()
            self.root.update()

    def select_colour_map_option(self, option, menu_button):
        self.selected_colour_map_option = option
        menu_button["text"] = option

        self.selected_image = self.root.image_controller.get_selected_image()

        if self.check_if_image_selected():
            self.selected_image.colour_map = self.selected_colour_map_option
            self.selected_image.update_image_render()
            self.root.update()

    def update_selected_scaling(self, option):
        self.selected_scaling_option = option
        self.scaling_dropdown["text"] = option

    def update_selected_colour_map(self, option):
        self.selected_colour_map_option = option
        self.colour_map_dropdown["text"] = option

    def check_if_image_selected(self):
        if self.selected_image is None:
            return False

        return True
