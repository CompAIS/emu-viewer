from dataclasses import dataclass
from typing import List

import astropy.io.votable as Votable


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
