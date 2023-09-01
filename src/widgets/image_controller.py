import ttkbootstrap as ttk
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib
import tkinter as tk

matplotlib.use("TkAgg")
import os


# Create Image Controller Frame
class ImageController(ttk.Frame):
    gridX = 0
    gridY = 0

    open_images = []

    def __init__(self, parent, notebook):
        ttk.Frame.__init__(self, parent)
        self.grid(column=0, row=1)

        self.notebook = notebook  # Store the reference to the notebook

        # Add open_image as an event listener to open file
        parent.menu_controller.open_file.add(self.open_image)

    def open_image(self, file_path):
        new_tab = tk.Frame(self.notebook)
        self.notebook.add(
            new_tab, text=os.path.basename(file_path)
        )  # Set tab title as image name

        new_image = ImageFrame(new_tab, file_path, self.gridX, self.gridY)
        self.open_images.append(new_image)

        if self.gridX > self.gridY:
            self.gridY += 1
            self.gridX = 0
        else:
            self.gridX += 1

        self.notebook.select(new_tab)  # Switch to the newly created tab

    def show_popup_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Compare", command=self.Compare_option)
        menu.add_command(label="Close", command=self.close_option)
        menu.post(event.x_root, event.y_root)

    def Compare_option(self):
        print("Compare option clicked")

    def close_option(self):
        # Close the current tab or frame
        selected_tab = self.notebook.select()
        self.notebook.forget(selected_tab)


# Create an Image Frame
class ImageFrame(ttk.Frame):
    image_file = None

    def __init__(self, parent, file_path, x, y):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.image_file = file_path
        self.grid(column=x, row=y)
        self.handle_image()

    def handle_image(self):
        # Read the .fits file
        hdu_list = fits.open(self.image_file)
        image_data = hdu_list[0].data

        # Apply logarithmic scaling to the image data
        log_stretch = LogStretch()
        scaled_data = log_stretch(image_data)

        # Create a matplotlib figure
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot()
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.margins(0, 0)
        ax.axis("off")

        # Render the scaled image data onto the figure
        cax = ax.imshow(scaled_data, cmap="gray", origin="lower")

        # Embed the matplotlib figure in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)

        # Bind right-click event to the canvas widget
        canvas.get_tk_widget().bind("<Button-3>", self.show_popup_menu)

    def show_popup_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Compare", command=self.compare_option)
        menu.add_command(label="Close", command=self.close_option)
        menu.post(event.x_root, event.y_root)

    def compare_option(self):
        file_name = filedialog.askopenfilename(
            title="Select image to compare",
            filetypes=(("Fits files", "*.fits"), ("All files", "*.*")),
        )

        if file_name == "":
            return

        # Read the .fits file for the compared image
        hdu_list = fits.open(file_name)
        image_data = hdu_list[0].data

        # Apply logarithmic scaling to the image data
        log_stretch = LogStretch()
        scaled_data = log_stretch(image_data)

        # Create a new Figure for the compared image
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot()
        fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        ax.margins(0, 0)
        ax.axis("off")
        cax = ax.imshow(scaled_data, cmap="gray", origin="lower")

        # Embed the new matplotlib figure in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=1, row=0)  # Place the new image to the right

    def close_option(self):
        # Close the current tab or frame
        self.parent.destroy()
