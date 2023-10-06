import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb


class ImageTableWidget(tk.Toplevel):
    _instance = None

    def __new__(cls, root):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Image Table")
        self.root = root
        self.resizable(0, 0)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.image_present = False

        self.image_num = 0  # Initialize the image number

        self.open_windows = []
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()

        self.image_table()  # Create the image table widget

        self.protocol(
            "WM_DELETE_WINDOW", self.root.widget_controller.close_image_table_widget
        )

    def image_table(self):
        table = tb.Frame(self, bootstyle="light")
        table.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        label = tk.Label(table, text="Image Table")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table, columns=("Num", "Image", "Coords Matching", "Render Matching")
        )
        self.tree.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.tree.heading("#0", text="Num")
        self.tree.heading("#1", text="Image")
        self.tree.heading("#2", text="Coords Matching")
        self.tree.heading("#3", text="Render Matching")
        self.tree.grid(column=0, row=1, sticky="nsew")
        for image in self.open_images:
            self.add_image(image.file_name)

    def add_image(self, image_name):
        self.image_num += 1
        # Extract the file name from the image_path
        self.tree.insert("", "end", values=(self.image_num, image_name, "", ""))

    # def check_image_open(self):
    # return self.image_present

    def remove_image(self):
        # if self.check_image_open():
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.update_image_numbers()

    # else:
    # tk.messagebox.showinfo("No Open Images", "There are no open images to remove.")

    def update_image_numbers(self):
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(i + 1,) + self.tree.item(item, "values")[1:])

    def update_images(self):
        self.selected_image = self.root.image_controller.get_selected_image()
        self.open_images = self.root.image_controller.get_images()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for image in self.open_images:
            self.add_image(image.file_name)

        self.root.update()


if __name__ == "__main__":
    root = tk.Tk()

    # Example: Create the ImageTableWidget
    image_table_widget = ImageTableWidget(root)

    # Example: Add images
    # image_table_widget.add_image("C:/Users/ayman/Downloads/Optical_r.fits")
    # image_table_widget.add_image("path/to/Image2.png")
    # image_table_widget.add_image("path/to/Image3.png")

    # Example: Remove an image
    # image_table_widget.remove_image()

    root.mainloop()
