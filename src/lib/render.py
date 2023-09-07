import os
import random
import string

import numpy as np
from astropy.io import fits
from matplotlib.figure import Figure


def save_file(image_file):
    """
    Renders the provided .fits file with the given configuration (TODO) to a .png file.

    Returns the filepath to the png file.
    """

    # Read the .fits file (assume that the image is [0]?)
    hdu_list = fits.open(image_file)
    hdu = hdu_list[0]

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    data = hdu.data.squeeze()

    # Apply logarithmic scaling to the image data
    # log_stretch = LogStretch()
    # data = log_stretch(data)

    vmin, vmax = np.nanpercentile(data, (0.5, 99.5))

    # Create a matplotlib figure
    fig = Figure(figsize=(5, 5), dpi=150)
    ax = fig.add_subplot()
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.axis("off")

    # Render the scaled image data onto the figure
    ax.imshow(data, cmap="inferno", origin="lower", vmin=vmin, vmax=vmax)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    # TODO this is leaking file storage
    file_path = f"tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    if os.path.exists(file_path + ".png"):
        os.remove(file_path + ".png")

    fig.savefig(file_path)
    print(f"file saved to {file_path}")
    hdu_list.close()

    return file_path + ".png"


if __name__ == "__main__":
    file = save_file("data/sample/Optical_r.fits")
    print(f"Saved to {file}")
    vips_resize(file, 3005)
