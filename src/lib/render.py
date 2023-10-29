import numpy as np
from matplotlib.figure import Figure


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


DPI = 150


# TODO move to utils
def get_size_inches(widget):
    return widget.winfo_width() / DPI, widget.winfo_height() / DPI


# 486, 176
def create_histogram_data(image_data, min_value, max_value, width_px=1, height_px=1):
    counts, bins = np.histogram(image_data, bins=20000, range=(min_value, max_value))

    return counts, bins


def create_histogram_graph(width_px=1, height_px=1):
    width_inches = width_px / DPI
    height_inches = height_px / DPI
    fig = Figure(figsize=(width_inches, height_inches), dpi=DPI)
    fig.patch.set_facecolor("#afbac5")
    ax = fig.add_subplot()
    ax.set_facecolor("#afbac5")
    fig.subplots_adjust(top=1, bottom=0.25, right=1, left=0, hspace=0, wspace=0)
    ax.tick_params(
        which="major",
        labelsize=5,
        labelleft=False,
        left=False,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.format_coord = lambda x, y: str(x)

    return fig


def draw_histogram_graph(fig, count, bins, vmin, vmax):
    ax = fig.axes[0]
    ax.clear()
    ax.set_yscale("log")

    ax.stairs(count, bins)
    ax.autoscale(enable=True, axis="both")

    fig = draw_histogram_lines(fig, vmin, vmax)

    return fig


def draw_histogram_lines(fig, vmin, vmax):
    ax = fig.axes[0]
    for line in ax.lines:
        line.remove()

    ax.axvline(vmin, color="red", label="Min", linestyle="solid", linewidth=0.5)
    ax.axvline(vmax, color="red", label="Max", linestyle="solid", linewidth=0.5)

    return fig
