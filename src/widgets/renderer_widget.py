import tkinter as tk

import ttkbootstrap as tb


class RendererWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Renderer Configuration")
        self.geometry("500x250")

        self.grid_rowconfigure(0, weight=2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0)

        self.histogram_graph()
        self.renderer_options()

    def histogram_graph(self):
        histogram = tb.Frame(self, bootstyle="light")
        histogram.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        histogram.grid_propagate(0)

        label = tb.Label(histogram, text="Histogram Graph", bootstyle="success")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

    def renderer_options(self):
        render = tb.Frame(self, width=100, bootstyle="light")
        render.grid(column=1, row=0, sticky=tk.NSEW, padx=10, pady=10)
        render.grid_propagate(0)

        button1 = tb.Button(render, text="Scaling", bootstyle="success")
        button1.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        button2 = tb.Button(render, text="Colour Map", bootstyle="success")
        button2.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
