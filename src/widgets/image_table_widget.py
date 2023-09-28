import os
import tkinter as tk
from tkinter import ttk


class ImageTableWidget(tk.Toplevel):
    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.title("Image Table")
        self.geometry("500x500")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_table()  # Create the image table widget

        self.image_num = 0  # Initialize the image number

    def image_table(self):
        table = tk.Frame(self)
        table.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)
        table.grid_propagate(0)

        label = tk.Label(table, text="Image Table")
        label.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table, columns=("Num", "Image", "Coords Matching", "Render Matching")
        )
        self.tree.heading("#1", text="Num")
        self.tree.heading("#2", text="Image")
        self.tree.heading("#3", text="Coords Matching")
        self.tree.heading("#4", text="Render Matching")
        self.tree.grid(column=0, row=1, sticky="nsew")

    def add_image(self, image_path):
        self.image_num += 1
        # Extract the file name from the image_path
        image_name = os.path.basename(image_path)
        self.tree.insert("", "end", values=(self.image_num, image_name, "", ""))

    def remove_image(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.update_image_numbers()

    def update_image_numbers(self):
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(i + 1,) + self.tree.item(item, "values")[1:])


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
