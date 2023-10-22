import astropy.visualization as vis
import matplotlib
import numpy as np
from matplotlib.figure import Figure
from scipy.ndimage.filters import gaussian_filter
from vispy import scene

PERCENTILES = [90, 95, 99, 99.5, 99.9, 100]


def create_figure(
    image_data, grid, view, wcs, colour_map, vmin, vmax, s, contour_levels
):
    view.camera.rect = (0, 0, image_data.shape[0], image_data.shape[1])

    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch() + vis.ManualInterval(vmin, vmax)
    elif s == "Log":
        stretch = vis.LogStretch() + vis.ManualInterval(vmin, vmax)
    elif s == "Sqrt":
        stretch = vis.SqrtStretch() + vis.ManualInterval(vmin, vmax)

    data = stretch(image_data)

    image = scene.Image(
        data=data, cmap=colour_map, parent=view.scene, texture_format=float
    )

    return image


# def create_figure(image_data, wcs, colour_map, vmin, vmax, s, contour_levels):
# fig = Figure(figsize=(5, 5), dpi=150)
# fig.patch.set_facecolor("#afbac5")

# ax = fig.add_subplot(projection=wcs)
# fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
# # Unsure whether to leave this or not
# # ax.coords[0].set_format_unit(u.deg)
# ax.tick_params(axis="both", which="major", labelsize=5)
# ax.set_xlabel("RA")
# ax.set_ylabel("DEC")

# def format_coord(x, y):
#     c = wcs.pixel_to_world(x, y)

#     decimal = c.to_string(style="decimal", precision=2).replace(" ", ", ")
#     sexigesimal = c.to_string(
#         style="hmsdms", sep=":", pad=True, precision=2
#     ).replace(" ", ", ")
#     # Yes, round, not floor.
#     pix = f"{round(x)}, {round(y)}"

#     return f"WCS: ({decimal}); ({sexigesimal}); Image: ({pix})"

# # https://matplotlib.org/stable/gallery/images_contours_and_fields/image_zcoord.html
# ax.format_coord = format_coord

# # Render the scaled image data onto the figure
# image = ax.imshow(
#     image_data, cmap=colour_map, origin="lower", norm=norm, interpolation="nearest"
# )

# cbar = fig.colorbar(image, shrink=0.5)
# tick_locator = ticker.MaxNLocator(nbins=10)
# cbar.locator = tick_locator
# cbar.ax.tick_params(labelsize=5)
# cbar.update_ticks()

# return fig, image


def create_figure_png(image_data, view):
    view.camera.rect = (0, 0, image_data.shape[0], image_data.shape[1])
    view.camera.flip = (0, 1, 0)

    image = scene.Image(data=image_data, parent=view.scene)

    return image


def update_image_norm(image, image_data, vmin, vmax, s):
    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch() + vis.ManualInterval(vmin, vmax)
    elif s == "Log":
        stretch = vis.LogStretch() + vis.ManualInterval(vmin, vmax)
    elif s == "Sqrt":
        stretch = vis.SqrtStretch() + vis.ManualInterval(vmin, vmax)

    data = stretch(image_data)

    image.set_data(data)

    return image


def update_image_cmap(image, colour_map):
    image.cmap = colour_map

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


def set_grid_lines(fig, visible):
    if visible:
        fig.axes[0].grid(linestyle="-", linewidth=0.2)
    else:
        fig.axes[0].grid(False)


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


def create_histogram(image_data, min_value, max_value):
    fig = Figure(figsize=(3.24, 1.1733333), dpi=150)
    fig.patch.set_facecolor("#afbac5")
    ax = fig.add_subplot(projection="HistogramAxes")
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

    ax.set_yscale("log")
    ax.format_coord = lambda x, y: str(x)

    counts, bins = np.histogram(image_data, bins=10000, range=(min_value, max_value))

    ax.stairs(counts, bins)

    return fig


def update_histogram_lines(fig, vmin, vmax, min_line, max_line):
    if min_line is not None:
        min_line.remove()

    if max_line is not None:
        max_line.remove()

    ax = fig.axes[0]
    min_line = ax.axvline(
        vmin, color="red", label="Min", linestyle="solid", linewidth=0.5
    )
    max_line = ax.axvline(
        vmax, color="red", label="Max", linestyle="solid", linewidth=0.5
    )

    return fig, min_line, max_line


# https://stackoverflow.com/questions/16705452/matplotlib-forcing-pan-zoom-to-constrain-to-x-axes
class HistogramAxes(matplotlib.axes.Axes):
    name = "HistogramAxes"

    def drag_pan(self, button, key, x, y):
        matplotlib.axes.Axes.drag_pan(self, button, "x", x, y)  # pretend key=='x'


matplotlib.projections.register_projection(HistogramAxes)
