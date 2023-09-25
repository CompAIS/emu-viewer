import tkinter as tk

import ttkbootstrap as tb


class RendererWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Renderer Configuration")
        self.resizable(0, 0)

        self.grid_rowconfigure(0, weight=2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0)

        self.histogram()
        self.render_options()

    def histogram(self):
        frame = tb.Frame(self, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.histogram_graph(frame)
        self.histogram_buttons(frame)

    def histogram_buttons(self, parent):
        button_90 = tb.Button(parent, text="90%", bootstyle="dark")
        button_90.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_95 = tb.Button(parent, text="95%", bootstyle="dark")
        button_95.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_99 = tb.Button(parent, text="99%", bootstyle="dark")
        button_99.grid(column=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_995 = tb.Button(parent, text="99.5%", bootstyle="dark")
        button_995.grid(column=3, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button_custom = tb.Button(parent, text="Custom", bootstyle="dark")
        button_custom.grid(column=4, row=0, sticky=tk.NSEW, padx=10, pady=10)

    def histogram_graph(self, parent):
        histogram = tb.Frame(parent, bootstyle="dark")
        histogram.grid(column=0, columnspan=5, row=1, sticky=tk.NSEW, padx=10, pady=10)

    def render_options(self):
        render = tb.Frame(self, width=100, bootstyle="light")
        render.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tb.Label(render, text="Render Options", bootstyle="inverse-light")
        label.grid(column=0, columnspan=2, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.min_options(render, 0, 1)

        self.max_options(render, 0, 2)

        self.scaling_options(render, 0, 3)

        self.colour_map_options(render, 0, 4)

    def min_options(self, parent, gridX, gridY):
        min_label = tb.Label(parent, text="Min", bootstyle="inverse-light")
        min_label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        min_entry = tb.Entry(parent, bootstyle="dark")
        min_entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

    def max_options(self, parent, gridX, gridY):
        max_label = tb.Label(parent, text="Max", bootstyle="inverse-light")
        max_label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        max_entry = tb.Entry(parent, bootstyle="dark")
        max_entry.grid(column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

    def scaling_options(self, parent, gridX, gridY):
        scaling_label = tb.Label(parent, text="Scaling", bootstyle="inverse-light")
        scaling_label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        scaling_dropdown = tb.Menubutton(
            parent, text="Scaling Options", bootstyle="dark"
        )
        scaling_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        scaling_dropdown_menu = tk.Menu(scaling_dropdown, tearoff=0)
        scaling_dropdown_menu.add_command(label="Render Option 1")
        scaling_dropdown_menu.add_command(label="Render Option 2")
        scaling_dropdown_menu.add_command(label="Render Option 3")
        scaling_dropdown_menu.add_command(label="Render Option 4")

        scaling_dropdown["menu"] = scaling_dropdown_menu

    def colour_map_options(self, parent, gridX, gridY):
        colour_map_label = tb.Label(
            parent, text="Colour Map", bootstyle="inverse-light"
        )
        colour_map_label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        colour_map_dropdown = tb.Menubutton(
            parent, text="Colour Map Options", bootstyle="dark"
        )
        colour_map_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        colour_map_dropdown_menu = tk.Menu(colour_map_dropdown, tearoff=0)
        colour_map_dropdown_menu.add_command(label="Colour Map Option 1")
        colour_map_dropdown_menu.add_command(label="Colour Map Option 2")
        colour_map_dropdown_menu.add_command(label="Colour Map Option 3")
        colour_map_dropdown_menu.add_command(label="Colour Map Option 4")

        colour_map_dropdown["menu"] = colour_map_dropdown_menu
