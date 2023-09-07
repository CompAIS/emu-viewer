import tkinter as tk
from tkinter import ttk


class ImageTableWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Image Table")
        self.geometry("500x250")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a frame for the table
        table_frame = ttk.Frame(self)
        table_frame.grid(row=0, column=0, sticky=tk.NSEW)

        # Create a table (Treeview) with two columns: "Num" and "Image Name"
        self.table = ttk.Treeview(
            table_frame, columns=("Num", "Image Name"), show="headings"
        )
        self.table.heading("Num", text="Num")
        self.table.heading("Image Name", text="Image Name")

        # Pack the table and set its column widths
        self.table.pack(fill=tk.BOTH, expand=True)
        self.table.column("Num", width=50)
        self.table.column("Image Name", width=200)

        # Initialize the image counter
        self.image_counter = 0

    def add_image(self, image_name):
        # Increment the image counter
        self.image_counter += 1
        num = self.image_counter

        # Add the image information to the table
        self.table.insert("", "end", values=(num, image_name))
