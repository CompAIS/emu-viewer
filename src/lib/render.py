import astropy.visualization as vis
import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure
from scipy.ndimage.filters import gaussian_filter


def create_figure(image_data, wcs, colour_map, min, max, s, contour_levels):
    fig = Figure(figsize=(5, 5), dpi=150)
    fig.patch.set_facecolor("#afbac5")
    ax = fig.add_subplot(projection=wcs)
    fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
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

    vmin, vmax = np.nanpercentile(image_data, (min, max))

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    # Render the scaled image data onto the figure
    image = ax.imshow(image_data, cmap=colour_map, origin="lower", norm=norm)

    cbar = fig.colorbar(image, shrink=0.5)
    tick_locator = ticker.MaxNLocator(nbins=10)
    cbar.locator = tick_locator
    cbar.ax.tick_params(labelsize=5)
    cbar.update_ticks()

    return fig, image


def update_image_norm(image, image_data, min, max, s):
    stretch = None

    if s == "Linear":
        stretch = vis.LinearStretch()
    elif s == "Log":
        stretch = vis.LogStretch()
    elif s == "Sqrt":
        stretch = vis.SqrtStretch()

    vmin, vmax = np.nanpercentile(image_data, (min, max))

    norm = vis.ImageNormalize(stretch=stretch, vmin=vmin, vmax=vmax)

    image.set_norm(norm)

    return image


def update_image_cmap(image, colour_map):
    image.set_cmap(colour_map)

    return image


def update_contours(fig, image_data, contour_levels, contour_set):
    if contour_set is not None:
        for contour in contour_set.collections:
            contour.remove()

    if contour_levels is None:
        return None

    print("I'm trying to contour!")

    # https://stackoverflow.com/questions/12274529/how-to-smooth-matplotlib-contour-plot
    image_data_smooth = gaussian_filter(image_data, 4)
    return fig.axes[0].contour(
        image_data_smooth,
        levels=contour_levels,
        colors="green",
        alpha=0.5,
        linewidths=0.5,
    )
