import astropy.visualization as vis
import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure
from scipy.ndimage.filters import gaussian_filter

PERCENTILES = [90, 95, 99, 99.5, 99.9, 100]


def create_figure(image_data, wcs, colour_map, vmin, vmax, s, contour_levels):
    fig = Figure(figsize=(5, 5), dpi=150)
    fig.patch.set_facecolor("#afbac5")

    ax = fig.add_subplot(projection=wcs)
    fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
    # Unsure whether to leave this or not
    # ax.coords[0].set_format_unit(u.deg)
    ax.tick_params(axis="both", which="major", labelsize=5)
    ax.set_xlabel("Ra")
    ax.set_ylabel("Dec")

    stretch = None

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

    return fig, image


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


def update_image_norm(image, vmin, vmax, s):
    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    image.set_norm(norm)

    return image


def update_image_cmap(image, colour_map):
    image.set_cmap(colour_map)

    return image


def draw_catalogue(
    fig, catalogue_set, ra_coords, dec_coords, size, colour_outline, colour_fill
):
    if catalogue_set is not None:
        catalogue_set.remove()

    ax = fig.axes[0]
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    catalogue_set = ax.scatter(
        ra_coords,
        dec_coords,
        s=size,
        edgecolor=colour_outline,
        facecolor=colour_fill,
        transform=ax.get_transform("world"),
    )

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    return fig, catalogue_set


def reset_catalogue(catalogue_set):
    if catalogue_set is not None:
        catalogue_set.remove()

    return None


def clear_contours(contour_set):
    if contour_set is not None:
        for contour in contour_set.collections:
            contour.remove()
    return None


def update_contours(
    fig,
    image_data,
    wcs,
    contour_levels,
    contour_set,
    gaussian_factor,
    line_colour,
    line_opacity,
    line_width,
):
    clear_contours(contour_set)

    if contour_levels is None:
        return None

    print("I'm trying to contour!")

    # https://stackoverflow.com/questions/12274529/how-to-smooth-matplotlib-contour-plot
    image_data_smooth = gaussian_filter(image_data, gaussian_factor)
    return fig.axes[0].contour(
        image_data_smooth,
        levels=contour_levels,
        colors=line_colour,
        alpha=line_opacity,
        linewidths=line_width,
        transform=fig.axes[0].get_transform(wcs),
    )


def get_percentiles(image_data):
    edges = []
    for percentile in PERCENTILES:
        edge = (100 - percentile) / 2
        lp, rp = edge, 100 - edge
        edges.extend([lp, rp])

    values = np.nanpercentile(image_data, tuple(edges))

    ret = {}
    for i, percentile in enumerate(PERCENTILES):
        ret[str(percentile)] = (values[i * 2], values[i * 2 + 1])

    return ret


def histogram(image_data):
    fig = Figure(figsize=(3.24, 1.2), dpi=150)
    fig.patch.set_facecolor("#afbac5")
    ax = fig.add_subplot()
    fig.subplots_adjust(top=1, bottom=0.25, right=1, left=0, hspace=0, wspace=0)
    ax.tick_params(
        which="major",
        labelsize=5,
        labelleft=False,
        left=False,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.set_yscale("log")

    counts, bins = np.histogram(
        image_data,
        bins=1000,
    )

    image = ax.stairs(counts, bins)

    return fig, image
