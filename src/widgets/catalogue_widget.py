import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.tableview import Tableview

import src.lib.catalogue_handler as catalogue_handler
from src.widgets.base_widget import BaseWidget


class CatalogueWidget(BaseWidget):
    label = "Catalogue"
    dropdown = True

    def __init__(self, root):
        super().__init__(self, root)
        self.resizable(True, True)
        self.geometry("{}x{}".format(850, 700))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.catalogue = None
        self.fields = None
        self.field_names = None
        self.field_data = None
        self.row_data = None

        self.chked_image = ImageTk.PhotoImage(
            Image.open("./resources/assets/checked_box.png")
        )
        self.unchked_image = ImageTk.PhotoImage(
            Image.open("./resources/assets/unchecked_box.png")
        )

        self.main_frame = tb.Frame(self, bootstyle="light")
        self.main_frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure((0, 1), weight=1)

        self.open_catalogue_xml()

        self.create_fields_table(self.main_frame, 0, 0)

        self.insert_fields_table()

        self.create_row_table(self.main_frame, 0, 1)

        self.create_controls()

    def open_catalogue_xml(self):
        file_name = tk.filedialog.askopenfilename(
            title="Select catalogue file",
            filetypes=(("xml files", "*.xml"), ("All files", "*.*")),
        )

        if file_name == "":
            self.close()

        self.catalogue = catalogue_handler.open_catalogue(file_name)
        self.fields = catalogue_handler.retrieve_fields(self.catalogue)
        self.field_names, self.field_data = catalogue_handler.retrieve_field_data(
            self.fields
        )
        self.row_data = catalogue_handler.retrieve_row_data(self.catalogue)

    def create_fields_table(self, parent, gridX, gridY):
        self.fields_table = ttk.Treeview(
            parent, height=10, columns=("name", "units", "datatype")
        )
        self.fields_table.grid(
            column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10, columnspan=2
        )
        self.fields_table.grid_propagate(True)
        style = ttk.Style(self.fields_table)
        style.configure("Treeview", rowheight="30")

        self.fields_table.tag_configure("checked", image=self.chked_image)
        self.fields_table.tag_configure("unchecked", image=self.unchked_image)

        self.fields_table.column("#0", width=100, stretch=False)
        self.fields_table.heading("#0", text="Display")
        self.fields_table.column("name", stretch=True)
        self.fields_table.heading("name", text="Name")
        self.fields_table.column("units", stretch=True)
        self.fields_table.heading("units", text="Units")
        self.fields_table.column("datatype", stretch=True)
        self.fields_table.heading("datatype", text="Datatype")

        self.fields_table.bind("<Button 1>", self.select_row)

    def insert_fields_table(self):
        for field in self.field_data:
            self.insert_fields_table_row(
                field["name"], field["unit"], field["datatype"]
            )

    def insert_fields_table_row(self, name, unit, datatype):
        self.fields_table.insert(
            "", tk.END, values=(name, unit, datatype), tags="unchecked"
        )

    def select_row(self, event):
        if self.fields_table is not None:
            row_id = self.fields_table.identify_row(event.y)
            tag = self.fields_table.item(row_id, "tags")[0]
            tags = list(self.fields_table.item(row_id, "tags"))
            tags.remove(tag)
            self.fields_table.item(row_id, tags=tags)

            field_name = self.fields_table.item(row_id)["values"][0]

            if tag == "checked":
                self.fields_table.item(row_id, tags="unchecked")
                self.hide_table_column(field_name)
            else:
                self.fields_table.item(row_id, tags="checked")
                self.show_table_column(field_name)

    def create_row_table(self, parent, gridX, gridY):
        self.main_table = Tableview(
            master=parent,
            coldata=self.field_names,
            rowdata=self.row_data,
            paginated=True,
            searchable=True,
            bootstyle="primary",
        )
        self.main_table.grid(column=gridX, row=gridY, sticky=tk.EW, padx=10, pady=10)
        self.main_table.grid_propagate(True)
        self.main_table.autofit_columns()

        for f_n in self.field_names:
            self.main_table.hide_selected_column(None, self.field_names.index(f_n))

    def hide_table_column(self, f_n):
        for n in self.field_names:
            if f_n == n["text"]:
                self.main_table.hide_selected_column(None, self.field_names.index(n))
                return

    def show_table_column(self, f_n):
        for n in self.field_names:
            if f_n == n["text"]:
                self.main_table.unhide_selected_column(None, self.field_names.index(n))
                return
