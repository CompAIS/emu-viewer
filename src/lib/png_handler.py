import numpy as np
from PIL import Image


def open_png_file(file_path):
    image_data = np.asarray(Image.open(file_path))

    return image_data
