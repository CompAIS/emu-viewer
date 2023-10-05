import tkinter as tk

import ttkbootstrap as tb


class StatisticsWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Statistics Table")
        self.geometry("500x250")
        self.root = root

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_table()

        self.protocol(
            "WM_DELETE_WINDOW", self.root.widget_controller.close_statistics_widget
        )

    def image_table(self):
        table = tb.Frame(self, bootstyle="light")
        table.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        table.grid_propagate(0)

        label = tb.Label(table, text="Statistics Table", bootstyle="success")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
