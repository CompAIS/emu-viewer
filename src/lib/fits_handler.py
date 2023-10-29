from typing import Dict, Tuple

import astropy.visualization as vis
import astropy.wcs.utils as sc
import numpy as np
import numpy.typing as npt
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from matplotlib import ticker
from matplotlib.figure import Figure
from matplotlib.image import AxesImage

from src import constants

ImageLimits = Tuple[SkyCoord, SkyCoord]


def open_fits_file(file_path: str) -> Tuple[npt.ArrayLike, fits.Header]:
    """Open and process a .fits file at file_path.

    Will always return the image at [0].

    :param str file_path: Path to the file to open.

    :return: a tuple of the image's data and the associated headers
    """

    fits_file = fits.open(file_path)

    hdu = fits_file[0]
    image_data_header = fits_file[0].header

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    image_data = hdu.data.squeeze()

    fits_file.close()

    return image_data, image_data_header


def create_figure_fits(
    image_data: npt.ArrayLike,
    image_wcs: WCS,
    colour_map: str,
    vmin: float,
    vmax: float,
    s: str,
) -> Tuple[Figure, AxesImage, ImageLimits]:
    """Create a figure from image_data with default options.

    :param image_data: numpy array with the image's data. Note that this should be float[][].
    :param image_wcs: the wcs of the image
    :param colour_map: the colour map to use
    :param vmin: the minimum value of the colour map - anything lower gets clipped
    :param vmax: the maximum value of the colour map - anything higher gets clipped
    :param s: the stretch / scaling of the image

    :return: the created figure, the image drawn on the figure, and the WCS limits of that image
    """

    fig = Figure(figsize=(5, 5), dpi=constants.DPI)
    fig.patch.set_facecolor("#afbac5")

    ax = fig.add_subplot(projection=image_wcs)
    fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
    # Unsure whether to leave this or not
    # ax.coords[0].set_format_unit(u.deg)
    ax.tick_params(axis="both", which="major", labelsize=5)
    ax.set_xlabel("RA")
    ax.set_ylabel("DEC")

    def format_coord(x, y):
        c = image_wcs.pixel_to_world(x, y)

        decimal = c.to_string(style="decimal", precision=2).replace(" ", ", ")
        sexigesimal = c.to_string(
            style="hmsdms", sep=":", pad=True, precision=2
        ).replace(" ", ", ")
        # Yes, round, not floor.
        pix = f"{round(x)}, {round(y)}"

        return f"WCS: ({decimal});\n WCS: ({sexigesimal});\n Image: ({pix})"

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_zcoord.html
    ax.format_coord = format_coord

    stretch = None

    # TODO enum-ify
    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    # Render the scaled image data onto the figure
    image = ax.imshow(
        image_data, cmap=colour_map, origin="lower", norm=norm, interpolation="nearest"
    )

    cbar = fig.colorbar(image, shrink=0.5)
    tick_locator = ticker.MaxNLocator(nbins=10)
    cbar.locator = tick_locator
    cbar.ax.tick_params(labelsize=5)
    cbar.update_ticks()

    return fig, image, get_limits(fig, image_wcs)


def update_image_norm(image, vmin, vmax, s):
    """Update the norm on the given image based on the provided options."""
    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    image.set_norm(norm)


def update_image_cmap(image: AxesImage, colour_map: str):
    """Update the colour map on the given image to the given colour map."""
    image.set_cmap(colour_map)


def set_grid_lines(fig, visible):
    if visible:
        fig.axes[0].grid(linestyle="-", linewidth=0.2)
    else:
        fig.axes[0].grid(False)


def get_percentiles(image_data: npt.ArrayLike) -> Dict[str, Tuple[float, float]]:
    """Calculate all the percentile values from the data in image_data.

    :param image_data: numpy array with the image's data. Note that this should be float[][].

    :return: a dict of percentiles (str version) to a tuple of (low, high)
        values. e.g. { "95": (2.5 value, 97.5 value) }
    """
    edges = []
    for percentile in constants.PERCENTILES:
        edge = (100 - percentile) / 2
        lp, rp = edge, 100 - edge
        edges.extend([lp, rp])

    values = np.nanpercentile(image_data, tuple(edges))

    ret = {}
    for i, percentile in enumerate(constants.PERCENTILES):
        ret[str(percentile)] = (values[i * 2], values[i * 2 + 1])

    return ret


def get_limits(fig: Figure, image_wcs: WCS) -> ImageLimits:
    """Get the limits of the plot, as a tuple of SkyCoords.

    :param fig: the figure
    :param image_wcs: the image's wcs object

    :return: the ImageLimits
    """
    ax = fig.axes[0]

    xlim_low, xlim_high = ax.get_xlim()
    ylim_low, ylim_high = ax.get_ylim()

    point1 = image_wcs.pixel_to_world(xlim_low, ylim_low)
    point2 = image_wcs.pixel_to_world(xlim_high, ylim_high)
    limits = (point1, point2)

    return limits


def set_limits(fig: Figure, image_wcs: WCS, limits: ImageLimits):
    """Set the limits on the plot from the given limits.

    :param fig: the figure
    :param image_wcs: the image's wcs object
    :param limits: the ImageLimits to set
    """

    ax = fig.axes[0]

    xlim_low, ylim_low = sc.skycoord_to_pixel(limits[0], image_wcs, mode="all")
    xlim_high, ylim_high = sc.skycoord_to_pixel(limits[1], image_wcs, mode="all")

    ax.set_xlim(xlim_low, xlim_high)
    ax.set_ylim(ylim_low, ylim_high)
