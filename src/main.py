import tkinter as tk
from tkinter import filedialog
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# Create Main Tkinter Window
class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("FITS Image Viewer")
        self.geometry("250x250")

        self.menu_controller = MenuBar(self)
        self.image_controller = ImageController(self)

        self.config(menu=self.menu_controller.menu)

    # Main run function for app
    def run(self):
        if self.menu_controller.file_name != "":
            print(self.menu_controller.file_name)
            file_name = self.menu_controller.file_name
            self.image_controller.open_image(file_name)
            self.menu_controller.file_name = ""

        # Do not remove or edit, required for run loop to function
        self.after(0, self.run)


# Create Menu bar for tkinter window
class MenuBar(tk.Frame):
    file_opened = False
    file_name = ""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0)

        self.menu = tk.Menu(self.parent)

        self.file_menu_creation()

    # Create file menu options
    def file_menu_creation(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open)
        file_menu.add_command(label="Exit", command=self.parent.quit)

    # Open command for option in menu
    def open(self):
        self.file_opened = True

        self.file_name = filedialog.askopenfilename(title="Select .fits file", initialdir="/",
                                                filetypes=(('Fits files', '*.fits'), ('All files', '*.*')))


# Create Image Controller Frame
class ImageController(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.grid(column=0, row=1)

    # Open image file based on path selected
    def open_image(self, file_path):
        # Read the .fits file
        image_file = file_path
        hdu_list = fits.open(image_file)
        image_data = hdu_list[0].data

        # Apply logarithmic scaling to the image data
        log_stretch = LogStretch()
        scaled_data = log_stretch(image_data)

        # Create a matplotlib figure
        fig = Figure(figsize=(5, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Render the scaled image data onto the figure
        cax = ax.imshow(scaled_data, cmap="gray", origin="lower")

        # Add a colorbar
        fig.colorbar(cax)

        # Embed the matplotlib figure in the tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0, row=0)


# Create an Image Frame
class ImageFrame(tk.Frame):
    def __init__(self, parent, file_path):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        text = tk.Label(self, text=file_path)
        text.grid(column=0, row=0)


# Run the main tkinter window
main_app = MainWindow()

main_app.after(1000, main_app.run)

main_app.mainloop()
