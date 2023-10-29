from astropy.io import fits
from numpy import typing as npt


def open_fits_file(file_path: str):
    """Open and process a .fits file at file_path.

    Will always return the image at [0].

    :param str file_path: Path to the file to open.

    :return: a tuple of the image's data and the associated headers
    """

    fits_file = fits.open(file_path)

    hdu = fits_file[0]
    image_data_header = fits_file[0].header

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    image_data = hdu.data.squeeze()

    fits_file.close()

    return image_data, image_data_header
