from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from astropy import wcs
from matplotlib.contour import QuadContourSet
from matplotlib.figure import Figure
from scipy.ndimage.filters import gaussian_filter


def generate_levels(mean: float, sigma: float, sigma_list: list[float]):
    """Generate levels to draw the contours at.

    Based on `sigma_list`, which is a multiplier on `sigma`, offset by mean.

    :param mean: the mean to use
    :param sigma: the sigma (standard deviation) to use
    :param sigma_list: the sigma list to use (corresponds to each level)
    """

    return [mean + sigma * x for x in sigma_list]


def get_sigma(image_data: npt.ArrayLike):
    """Calculate the sigma based on the data clipped at 2.5 times the standard deviation.

    Taken with modifications with permission from Kieran Luken.

    :param image_data: the data to calculate from. Should be a float[][]
    """
    clipped_image = np.copy(image_data)
    clip_level = 2.5 * np.nanstd(clipped_image)
    clipped_image[np.where(clipped_image > clip_level)] = np.nan
    return np.nanstd(clipped_image)

    # if you want no clipping, use this!
    # return np.nanstd(image_data)


@dataclass
class RenderContourOptions:
    """Determines where and how to draw contours.

    :param data_source: numpy array with the data to use. Note that this should
        be float[][].
    :param data_source_wcs: the wcs object of the data sourjce
    :param contour_levels: the thresholds to draw contour lines at
    :param gaussian_factor: how much to smooth the data before generating contours on
    :param line_colour: the colour of the contour lines
    :param line_opacity: the opacity of the contour lines
    :param line_width: the width of the contour lines
    """

    data_source: npt.ArrayLike
    data_source_wcs: wcs.WCS
    contour_levels: list[float]
    gaussian_factor: float
    line_colour: str
    line_opacity: float
    line_width: float


def clear_contours(contour_set: QuadContourSet):
    """Remove all contours from the axes.

    :param contour_set: the set of contours to remove from
    """
    if contour_set is not None:
        for contour in contour_set.collections:
            contour.remove()


def update_contours(
    fig: Figure, contour_set: QuadContourSet, options: RenderContourOptions
):
    """Draw contours onto the 0th axes on the given figure with the given
        options.

    Will replace the existing contour_set when provided.

    :param fig: the figure to draw on
    :param contour_set: the existing contour set, passed here to clear
    :param options: options given to render the contour as
    """

    clear_contours(contour_set)

    print("I'm trying to contour!")
    options.contour_levels.sort()

    # https://stackoverflow.com/questions/12274529/how-to-smooth-matplotlib-contour-plot
    data_smooth = gaussian_filter(options.data_source, options.gaussian_factor)
    return fig.axes[0].contour(
        data_smooth,
        levels=options.contour_levels,
        colors=options.line_colour,
        alpha=options.line_opacity,
        linewidths=options.line_width,
        transform=fig.axes[0].get_transform(options.data_source_wcs),
    )
