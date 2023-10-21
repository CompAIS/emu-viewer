import numpy as np


def generate_levels(mean, sigma, sigma_list):
    """
    Generate levels to draw the contours at.

    Based on `sigma_list`, which is a multiplier on `sigma`, offset by mean.
    """

    return [mean + sigma * x for x in sigma_list]


def get_sigma(image_data):
    """
    Calculate the sigma based on data clipped at 2.5 times the standard deviation.

    Taken with modifications with permission from Kieran Lukan.
    """
    clipped_image = np.copy(image_data)
    clip_level = 2.5 * np.nanstd(clipped_image)
    clipped_image[np.where(clipped_image > clip_level)] = np.nan
    return np.nanstd(clipped_image)

    # if you want no clipping, use this!
    # return np.nanstd(image_data)
