import astropy.visualization as vis
import numpy as np
from matplotlib.figure import Figure


def create_figure(image_data, wcs, colour_map, min, max, s):
    fig = Figure(figsize=(5, 5), dpi=150)
    ax = fig.add_subplot(projection=wcs)
    fig.subplots_adjust(top=0.95, bottom=0.05, right=0.95, left=0.2, hspace=0, wspace=0)

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
    fig.colorbar(image)

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
