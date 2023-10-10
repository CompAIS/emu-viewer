from dataclasses import dataclass

import astropy.io.votable as Votable


@dataclass
class FieldsData:
    name: str = ""
    unit: str = ""
    datatype: str = ""


def open_catalogue(file_name):
    catalogue = Votable.parse_single_table(file_name)

    return catalogue


def retrieve_fields(catalogue):
    fields_params = []
    for f in catalogue.iter_fields_and_params():
        if type(f) is not Votable.tree.Param:
            fields_params.append(f)

    fields = []
    for f_p in fields_params:
        fields.append(f_p)

    return fields


def retrieve_field_data(fields):
    field_names = []
    field_data = []
    for f in fields:
        f_n = {"text": f.name}
        f_d = {
            "name": f.name,
            "unit": f.unit,
            "datatype": f.datatype,
        }
        field_names.append(f_n)
        field_data.append(f_d)

    return field_names, field_data


def retrieve_row_data(catalogue):
    row_data = catalogue.array

    return row_data
