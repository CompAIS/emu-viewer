import os
import random
import string

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
    fig = Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot()
    fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    ax.margins(0, 0)
    ax.axis("off")

    # Render the scaled image data onto the figure
    ax.imshow(data, cmap="inferno", origin="lower", vmin=vmin, vmax=vmax)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    # todo this is leaking file storage
    file_path = f"tmp/{''.join(random.choices(string.ascii_lowercase, k=10))}"
    fig.savefig(file_path)

    return file_path + ".png"


if __name__ == "__main__":
    print(f"Saved to {save_file('data/sample/Optical_r.fits')}")
