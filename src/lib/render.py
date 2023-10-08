import astropy.units as u
import astropy.visualization as vis
import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure


def create_figure(image_data, wcs, colour_map, min, max, s):
    fig = Figure(figsize=(5, 5), dpi=150)
    fig.patch.set_facecolor("#afbac5")

    ax = fig.add_subplot(projection=wcs)
    fig.subplots_adjust(top=0.95, bottom=0.2, right=0.95, left=0.2, hspace=0, wspace=0)
    ax.coords[0].set_format_unit(u.deg)
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


def draw_catalogue(fig, ra_coords, dec_coords):
    ax = fig.axes[0]
    ax.scatter(
        ra_coords,
        dec_coords,
        s=25,
        edgecolor="green",
        facecolor=None,
        transform=ax.get_transform("icrs"),
    )

    catalogue_set = None

    return fig, catalogue_set


def reset_catalogue(fig, catalogue_set):
    if catalogue_set is not None:
        catalogue_set.remove()
        catalogue_set = None

    return fig, catalogue_set
