from dataclasses import dataclass
from typing import List

import astropy.io.votable as Votable
from matplotlib.collections import PathCollection
from matplotlib.figure import Figure


@dataclass
class FieldData:
    name: str = ""
    unit: str = ""
    datatype: str = ""


def open_catalogue(file_path: str) -> Votable.tree.Table:
    """Open a catalogue file.

    :param file_path: Path to the catalogue file to open
    """
    return Votable.parse_single_table(file_path)


def retrieve_fields(catalogue: Votable.tree.Table) -> List[Votable.tree.Field]:
    """Retrieve all of the fields in a catalogue table.

    :return: the list of fields
    """

    fields = []
    for f in catalogue.iter_fields_and_params():
        if type(f) is not Votable.tree.Param:
            fields.append(f)

    return fields


@dataclass
class RenderCatalogueOptions:
    """Determines where and how to draw a catalogue."""

    ra_coords: List[float]
    dec_coords: List[float]
    size: float
    colour_outline: str
    colour_fill: str


def clear_catalogue(catalogue_set: PathCollection):
    """Remove all paths from the axes."""
    if catalogue_set is not None:
        catalogue_set.remove()


def draw_catalogue(
    fig: Figure, catalogue_set: PathCollection, options: RenderCatalogueOptions
):
    """Draw a catalogue onto the 0th axes on the given figure with the given
        options.

    Will replace the existing catalogue_set when provided.

    :param fig: the figure to draw on
    :param catalogue_set: the existing catalogue markers, passed here to clear
    :param options: options given to render the catalogue as
    """
    clear_catalogue(catalogue_set)

    ax = fig.axes[0]

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    catalogue_set = ax.scatter(
        options.ra_coords,
        options.dec_coords,
        s=options.size,
        edgecolor=options.colour_outline,
        facecolor=options.colour_fill,
        transform=ax.get_transform("world"),
    )

    # apply the saved lims
    # we do this since ax.scatter will try to zoom out the view so all markers
    # can be seen, but we don't want this
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    return fig, catalogue_set
