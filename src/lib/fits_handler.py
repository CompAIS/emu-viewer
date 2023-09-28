from astropy.io import fits


def open_fits_file(file_path):
    fits_file = fits.open(file_path)

    hdu = fits_file[0]
    image_data_header = fits_file[0].header

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    image_data = hdu.data.squeeze()

    fits_file.close()

    return image_data, image_data_header
