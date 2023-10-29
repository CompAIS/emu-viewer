import numpy as np
from matplotlib.figure import Figure
from PIL import Image


def open_png_file(file_path):
    image_data = np.asarray(Image.open(file_path))

    return image_data


def create_figure_png(image_data):
    fig = Figure(figsize=(5, 5), dpi=150)
    fig.patch.set_facecolor("#afbac5")
    ax = fig.add_subplot()
    fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
    ax.tick_params(
        labelbottom=False,
        labeltop=False,
        labelleft=False,
        labelright=False,
        bottom=False,
        top=False,
        left=False,
        right=False,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")

    image = ax.imshow(image_data)

    return fig, image
