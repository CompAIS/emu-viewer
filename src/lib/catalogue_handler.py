from astropy.table import Table


def open_catalogue(file_name):
    catalogue = Table.read(file_name)

    return catalogue
