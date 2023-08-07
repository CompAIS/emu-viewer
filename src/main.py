import tkinter as tk
from astropy.io import fits
from astropy.visualization import LogStretch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Read the .fits file
image_file = './data/sample/Optical_r.fits'
hdu_list = fits.open(image_file)
image_data = hdu_list[0].data

# Apply logarithmic scaling to the image data
log_stretch = LogStretch()
scaled_data = log_stretch(image_data)

# Create a tkinter window
root = tk.Tk()
root.title("FITS Image Viewer")

# Create a matplotlib figure
fig = Figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)

# Render the scaled image data onto the figure
cax = ax.imshow(scaled_data, cmap='gray', origin='lower')

# Add a colorbar
fig.colorbar(cax)

# Embed the matplotlib figure in the tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Run the tkinter main loop
root.mainloop()