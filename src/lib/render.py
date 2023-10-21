import astropy.visualization as vis
import astropy.wcs.utils as sc
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

    def format_coord(x, y):
        c = wcs.pixel_to_world(x, y)

        decimal = c.to_string(style="decimal", precision=2).replace(" ", ", ")
        sexigesimal = c.to_string(
            style="hmsdms", sep=":", pad=True, precision=2
        ).replace(" ", ", ")
        # Yes, round, not floor.
        pix = f"{round(x)}, {round(y)}"

        return f"WCS: ({decimal}); ({sexigesimal}); Image: ({pix})"

    # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_zcoord.html
    ax.format_coord = format_coord

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

    xlim_low, xlim_high = ax.get_xlim()
    ylim_low, ylim_high = ax.get_ylim()

    point1 = wcs.pixel_to_world(xlim_low, ylim_low)
    point2 = wcs.pixel_to_world(xlim_high, ylim_high)
    limits = [point1, point2]

    return fig, image, limits


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


def set_limits(fig, wcs, limits):
    ax = fig.axes[0]

    xlim_low, ylim_low = sc.skycoord_to_pixel(limits[0], wcs, mode="all")
    xlim_high, ylim_high = sc.skycoord_to_pixel(limits[1], wcs, mode="all")

    ax.set_xlim(xlim_low, xlim_high)
    ax.set_ylim(ylim_low, ylim_high)

    return fig


def get_limits(fig, wcs):
    ax = fig.axes[0]

    xlim_low, xlim_high = ax.get_xlim()
    ylim_low, ylim_high = ax.get_ylim()

    point1 = wcs.pixel_to_world(xlim_low, ylim_low)
    point2 = wcs.pixel_to_world(xlim_high, ylim_high)
    limits = [point1, point2]

    return limits
