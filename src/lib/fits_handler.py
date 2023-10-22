from astropy.io import fits


def open_fits_file(file_path):
    fits_file = fits.open(file_path)

    hdu = fits_file[0]
    image_data_header = fits_file[0].header

    # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
    image_data = hdu.data.squeeze()

    fits_file.close()

    return image_data, image_data_header


def pixel_to_coord(wcs, style, xory, coord):
    """wrapper function"""
    x, y = (coord, 0) if xory == "x" else (0, coord)
    c = wcs.pixel_to_world(x, y)  # TODO can we convert one at a time.
    if style == "decimal":
        xdec, ydec = c.to_string(style=style, precision=3).split(" ")
    else:  # hmsdms
        xdec, ydec = c.to_string(style=style, sep=":", pad=True, precision=2).split(" ")

    return xdec if xory == "x" else ydec
