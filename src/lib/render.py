import os
import random
import string

import pyvips as vips
from astropy.io import fits
from matplotlib.figure import Figure


def save_file(image_file):
    """
    Renders the provided .fits file with the given configuration (TODO) to a .png file.

    Returns the filepath to the png file.
    """

    # Read the .fits file
    hdu_list = fits.open(image_file)
    data = hdu_list[0].data

    # Apply logarithmic scaling to the image data
    # log_stretch = LogStretch()
    # data = log_stretch(data)

    # vmin = np.percentile(data, 2.5)
    # vmax = np.percentile(data, 97.5)
    vmin, vmax = 0, 1500
    print(vmin, vmax)

    # Create a matplotlib figure
    fig = Figure(figsize=(5, 5), dpi=300)
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
    fig.savefig(file_path)

    return file_path + ".png"


def vips_resize(file_path, size):
    vips_raw_img = vips.Image.new_from_file(file_path)
    scale = size / vips_raw_img.width
    print(vips_raw_img.width, vips_raw_img.height)
    new = vips_raw_img.resize(scale)
    print(new.width, new.height)


if __name__ == "__main__":
    file = save_file("data/sample/Optical_r.fits")
    print(f"Saved to {file}")
    vips_resize(file, 3005)
