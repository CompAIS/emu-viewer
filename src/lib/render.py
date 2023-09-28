import os
import random
import string

import astropy.visualization as vis
import numpy as np
from matplotlib.figure import Figure


def save_file(fits_file, colour_map, min, max, s):
    """
    Renders the provided .fits file with the given configuration (TODO) to a .png file.

    Returns the filepath to the png file.
    """

    hdu = fits_file[0]

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    data = hdu.data.squeeze()

    # Create a matplotlib figure
    fig = Figure(figsize=(5, 5), dpi=150)
    ax = fig.add_subplot()
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.axis("off")

    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    vmin, vmax = np.nanpercentile(data, (min, max))

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    # Render the scaled image data onto the figure
    ax.imshow(data, cmap=colour_map, origin="lower", norm=norm)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    # TODO this is leaking file storage
    file_path = f"tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    if os.path.exists(file_path + ".png"):
        os.remove(file_path + ".png")

    fig.savefig(file_path)
    print(f"file saved to {file_path}")

    return file_path + ".png"


def create_render(image_data, colour_map, min, max, s):
    # Create a matplotlib figure
    fig = Figure(figsize=(5, 5), dpi=150)
    ax = fig.add_subplot()
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.axis("off")

    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    vmin, vmax = np.nanpercentile(image_data, (min, max))

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    # Render the scaled image data onto the figure
    image = ax.imshow(image_data, cmap=colour_map, origin="lower", norm=norm)

    png_file_path = save_temp_file(fig)

    return png_file_path


def update_colour_map(image, colour_map):
    image.set_cmap(colour_map)

    return image


def update_norm(image, image_data, min, max, s):
    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    vmin, vmax = np.nanpercentile(image_data, (min, max))

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    image.set_norm(norm)

    return image


def save_temp_file(fig):
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    # TODO this is leaking file storage
    file_path = f"tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    if os.path.exists(file_path + ".png"):
        os.remove(file_path + ".png")

    fig.savefig(file_path)
    print(f"file saved to {file_path}")

    return file_path + ".png"
