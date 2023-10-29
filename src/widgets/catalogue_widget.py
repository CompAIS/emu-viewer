import os
import tkinter as tk
from functools import partial
from tkinter import filedialog, ttk

import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
from ttkbootstrap.tableview import Tableview

import src.lib.catalogue_handler as catalogue_handler
from src.constants import ASSETS_FOLDER
from src.controllers import image_controller as ic
from src.widgets.base_widget import BaseWidget


class CatalogueWidget(BaseWidget):
    label = "Catalogue"
    dropdown = True

    def __init__(self, root):
        super().__init__(root)
        self.resizable(True, True)
        self.geometry("{}x{}".format(850, 775))
        self.root = root

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.catalogue = None
        self.fields = None
        self.field_names = None
        self.field_data = None
        self.row_data = None

        self.selected_ra = ""
        self.selected_dec = ""

        self.size = 25
        self.colour_outline = "green"
        self.colour_fill = "none"

        chked_image_path = os.path.join(ASSETS_FOLDER, "checked_box.png")
        unchked_image_path = os.path.join(ASSETS_FOLDER, "unchecked_box.png")

        self.chked_image = ImageTk.PhotoImage(Image.open(chked_image_path))
        self.unchked_image = ImageTk.PhotoImage(Image.open(unchked_image_path))

        try:
            self.create_tables()
        except Exception:
            self.destroy()
            raise Exception("Widget no longer exists")

        self.create_controls()

    def create_tables(self):
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
        file_name = filedialog.askopenfilename(
            title="Select catalogue file",
            filetypes=(("xml files", "*.xml"), ("All files", "*.*")),
        )

        if file_name == "":
            raise Exception("Filename is empty")

        self.catalogue = catalogue_handler.open_catalogue(file_name)
        self.fields = catalogue_handler.retrieve_fields(self.catalogue)
        self.field_names, self.field_data = catalogue_handler.retrieve_field_data(
            self.fields
        )
        self.row_data = catalogue_handler.retrieve_row_data(self.catalogue)

    def create_fields_table(self, parent, gridX, gridY):
        self.fields_table = ttk.Treeview(
            parent, height=11, columns=("name", "units", "datatype")
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

            if row_id == "":
                return

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

    def create_controls(self):
        controls_frame = tb.Frame(self, bootstyle="light")
        controls_frame.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        controls_frame.rowconfigure(0, weight=1)
        controls_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.ra_dropdown_setup(controls_frame, "RA", "No options set", 0, 0)

        self.dec_dropdown_setup(controls_frame, "DEC", "No options set", 2, 0)

        self.buttons(controls_frame, 4, 0)

    def ra_dropdown_setup(self, parent, text, ra, gridX, gridY):
        ra_options = self.generate_ra_options()

        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.ra_dropdown = tb.Menubutton(parent, text=ra, bootstyle="dark")
        self.ra_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.ra_dropdown, tearoff=0)

        for option in ra_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_ra, option),
            )

        self.ra_dropdown["menu"] = dropdown_menu

    def generate_ra_options(self):
        options = []

        for n in self.field_data:
            if (
                n["name"].startswith("ra")
                or n["name"].endswith("ra")
                or n["name"].endswith("RA")
            ):
                options.append(n["name"])

        return options

    def select_ra(self, option):
        self.selected_ra = option
        self.ra_dropdown["text"] = option

    def dec_dropdown_setup(self, parent, text, dec, gridX, gridY):
        dec_options = self.generate_dec_options()

        label = tb.Label(parent, text=text, bootstyle="inverse-light")
        label.grid(column=gridX, row=gridY, sticky=tk.NSEW, padx=10, pady=10)

        self.dec_dropdown = tb.Menubutton(parent, text=dec, bootstyle="dark")
        self.dec_dropdown.grid(
            column=gridX + 1, row=gridY, sticky=tk.NSEW, padx=10, pady=10
        )

        dropdown_menu = tk.Menu(self.dec_dropdown, tearoff=0)

        for option in dec_options:
            dropdown_menu.add_command(
                label=option,
                command=partial(self.select_dec, option),
            )

        self.dec_dropdown["menu"] = dropdown_menu

    def generate_dec_options(self):
        options = []

        for n in self.field_data:
            if (
                n["name"].startswith("dec")
                or n["name"].endswith("dec")
                or n["name"].endswith("DEC")
            ):
                options.append(n["name"])

        return options

    def select_dec(self, option):
        self.selected_dec = option
        self.dec_dropdown["text"] = option

    def buttons(self, parent, gridX, gridY):
        button_frame = tb.Frame(parent, bootstyle="light")
        button_frame.grid(column=gridX, row=gridY, sticky=tk.SE, padx=10, pady=10)
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure((0, 1, 2), weight=1)

        config_button = tb.Button(
            button_frame,
            bootstyle="dark",
            text="Config",
            command=self.config_command,
        )
        config_button.grid(column=0, row=0, sticky=tk.SE, padx=10)

        reset_button = tb.Button(
            button_frame,
            bootstyle="warning",
            text="Reset",
            command=self.reset_command,
        )
        reset_button.grid(column=1, row=0, sticky=tk.SE, padx=10)

        apply_button = tb.Button(
            button_frame,
            bootstyle="success",
            text="Apply",
            command=self.apply_command,
        )
        apply_button.grid(column=2, row=0, sticky=tk.SE, padx=10)

    def config_command(self):
        config = tk.Toplevel(self)
        config.title("Catalogue Config")
        config.resizable(False, False)

        config.columnconfigure(0, weight=1)
        config.rowconfigure(0, weight=1)

        frame = tb.Frame(config, bootstyle="light")
        frame.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        config.columnconfigure((0, 1), weight=1)
        config.rowconfigure((0, 1, 2, 3), weight=1)

        title_label = tb.Label(frame, text="Config Options", bootstyle="inverse-light")
        title_label.grid(
            column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10
        )

        size_label = tb.Label(frame, text="Size (25)", bootstyle="inverse-light")
        size_label.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

        size_slider = tb.Scale(
            frame,
            from_=5,
            to=100,
            command=partial(self.set_size, size_label),
            value=self.size,
        )
        size_slider.grid(column=1, row=1, padx=10, pady=10, sticky=tk.NSEW)

        outline_label = tb.Label(
            frame, text="Colour outline", bootstyle="inverse-light"
        )
        outline_label.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)

        box_size = 23
        self.outline_button = tk.Canvas(
            frame, bg=self.colour_outline, width=box_size + 1, height=box_size + 1
        )
        self.outline_button.grid(column=1, row=2, sticky=tk.W, padx=10, pady=10)
        self.outline_rect = self.outline_button.create_rectangle(
            0, 0, box_size, box_size, outline="black", fill=self.colour_outline
        )
        self.outline_button.bind("<Button-1>", self.set_colour_outline)

        apply_button = tb.Button(
            frame,
            bootstyle="success",
            text="Apply",
            command=partial(self.apply_config, config),
        )
        apply_button.grid(column=1, row=3, sticky=tk.SE, padx=10, pady=10)

        config.grab_set()

    def set_size(self, size_label, value):
        value = float(value)
        self.size = value
        size_label["text"] = f"Size ({value:1.2f})"

    def set_colour_outline(self, _evt):
        cd = ColorChooserDialog(
            initialcolor=self.colour_outline, title="Choose Outline Colour"
        )
        cd.show()
        self.after(1, lambda: self.focus_set())

        if cd.result is None:
            return

        self.colour_outline = cd.result.hex
        self.outline_button.itemconfig(self.outline_rect, fill=self.colour_outline)

    def apply_config(self, config):
        config.destroy()

    def reset_command(self):
        self.selected_ra = ""
        self.selected_dec = ""
        self.ra_dropdown["text"] = "Nothing selected"
        self.dec_dropdown["text"] = "Nothing selected"

        if ic.get_selected_image().catalogue_set is None:
            return

        ic.get_selected_image().reset_catalogue()

    def apply_command(self):
        if self.selected_ra == "" or self.selected_dec == "":
            return

        ra_coords = []
        for data in self.row_data[self.selected_ra]:
            ra_coords.append(data)

        dec_coords = []
        for data in self.row_data[self.selected_dec]:
            dec_coords.append(data)

        if ic.get_selected_image().image_wcs is None:
            return

        ic.get_selected_image().draw_catalogue(
            ra_coords, dec_coords, self.size, self.colour_outline, self.colour_fill
        )
