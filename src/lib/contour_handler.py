import numpy as np

from src.lib.fits_handler import open_fits_file


def generate_levels(image_data, mean, sigma, sigma_list):
    return [158.91, 314.95, 627.02]


if __name__ == "__main__":
    image_data, image_data_header = open_fits_file("resources/data/Optical_r.fits")

    def calculate_noise():
        """Function to calculate the noise of an image. Clips the image at 2.5 times the standard deviation of the image, then
        recalculates the standard deviation based on the clipped image. Based on the technique used by the Miriad 'sigest' task:
        https://www.atnf.csiro.au/computing/software/miriad/doc/sigest.html
        """
        clipped_image = np.copy(image_data)
        clip_level = 2.5 * np.nanstd(clipped_image)
        clipped_image[np.where(clipped_image > clip_level)] = np.nan
        return np.nanstd(clipped_image)

    # contour_levels = np.ones_like(image_data)
    # image_noise = calculate_noise()
    # contour_levels[image_data < 2 * image_noise] = 0
    print(np.mean(image_data))
    print(np.nanstd(image_data))

    # I need:
    # Mean
    # Sigma
    # Sigma list
    # Which will give me
    # Levels
