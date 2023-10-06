import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as tb
from ttkbootstrap.tableview import Tableview

import src.lib.catalogue_handler as catalogue_handler
from src.widgets.base_widget import BaseWidget


class CatalogueWidget(BaseWidget):
    label = "Catalogue"
    dropdown = True

    def __init__(self, root):
        BaseWidget.__init__(self, root)
        self.geometry("800x400")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        button = tb.Button(
            self,
            text="Load file",
            bootstyle="dark",
            command=self.open_catalogue_xml,
        )
        button.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

    def open_catalogue_xml(self):
        file_name = filedialog.askopenfilename(
            title="Select catalogue file",
            filetypes=(("xml files", "*.xml"), ("All files", "*.*")),
        )

        self.catalogue_data = catalogue_handler.open_catalogue(file_name)

        self.window = tb.Frame(self, bootstyle="light")
        self.window.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.create_table(self.window, 0, 0)

    def create_table(self, parent, gridX, gridY):
        rowdata = []
        for i in range(len(self.catalogue_data)):
            rowdata.append(self.catalogue_data[i])

        dt = Tableview(
            master=parent,
            coldata=self.catalogue_data.colnames,
            rowdata=rowdata,
            paginated=True,
            searchable=True,
            bootstyle="primary",
        )
        dt.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)
        dt.autofit_columns()
