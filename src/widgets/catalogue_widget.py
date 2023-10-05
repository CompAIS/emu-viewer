import tkinter as tk


class CatalogueWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Catalogue")
        self.resizable(0, 0)
        self.root = root

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.protocol(
            "WM_DELETE_WINDOW", self.root.widget_controller.close_catalogue_widget
        )
