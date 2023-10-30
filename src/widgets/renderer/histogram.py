from typing import Tuple

import numpy as np
import numpy.typing as npt
from matplotlib.figure import Figure

from src import constants


def create_histogram_data(
    image_data: npt.ArrayLike, min_value: float, max_value: float
) -> Tuple[npt.ArrayLike, npt.ArrayLike]:
    """Creates the data for the histogram from the given image_data.

    :param image_data: numpy array with the image's data. Note that this should be float[][].
    :param min_value: lower bound of the histogram
    :param max_value: upper bound of the histogram

    :return: tuple of (the values of the histogram, the edges of the bins)
    """

    return np.histogram(image_data, bins=20000, range=(min_value, max_value))


def create_histogram_graph(width_px=1, height_px=1):
    """Creates a base histogram figure, unspecific to any image data.

    TODO width_px and height_px necessary?
    """

    width_inches = width_px / constants.DPI
    height_inches = height_px / constants.DPI

    # we want to smartly generate the size here so it doesn't change the size
    # of the render config widget and so that it fits in nicely
    fig = Figure(figsize=(width_inches, height_inches), dpi=constants.DPI)
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
    # the value at any point is the same as the x-coordinate - we do not care about
    # the y value (which is frequency)
    ax.format_coord = lambda x, y: str(x)

    return fig


def draw_histogram_graph(
    fig: Figure, count: npt.ArrayLike, bins: npt.ArrayLike, vmin: float, vmax: float
):
    """Draw the histogram on the given figure, given some data

    :param fig: the figure
    :param count: the histogram frequencies (generated via create_histogram_data)
    :param bins: the bin edges (generated via create_histogram_data)
    :param vmin: the set vmin value, which draws a red line (representing the
        lower bound in the colour map)
    :param vmax: the set vmin value, which draws a red line (representing the
        lower bound in the colour map)
    """
    ax = fig.axes[0]
    ax.clear()
    ax.set_yscale("log")

    ax.stairs(count, bins)
    ax.autoscale(enable=True, axis="both")

    fig = draw_histogram_lines(fig, vmin, vmax)

    return fig


def draw_histogram_lines(fig: Figure, vmin: float, vmax: float):
    """Draw the vmin / vmax lines on the image.

    :param fig: the figure
    :param vmin: the set vmin value, which draws a red line (representing the
        lower bound in the colour map)
    :param vmax: the set vmin value, which draws a red line (representing the
        lower bound in the colour map)
    """

    ax = fig.axes[0]
    for line in ax.lines:
        line.remove()

    ax.axvline(vmin, color="red", label="Min", linestyle="solid", linewidth=0.5)
    ax.axvline(vmax, color="red", label="Max", linestyle="solid", linewidth=0.5)

    return fig
