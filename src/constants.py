import os
import platform
import sys
import tkinter as tk
from PIL import Image, ImageTk

PERCENTILES = [90, 95, 99, 99.5, 99.9, 100]
DPI = 150

# loading images and such

# https://stackoverflow.com/questions/22472124/what-is-sys-meipass-in-python
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running from a compiled executable
    ASSETS_FOLDER = os.path.join(sys._MEIPASS, "resources", "assets")
elif platform.system() == "Linux":
    ASSETS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "assets"))
else:
    ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "resources", "assets")

ICONPNG_PATH = os.path.join(ASSETS_FOLDER, "favicon-32x32.png")
ICONPNG = None
FAVICON = None


def load_images():
    """
    Load images once we have tk available. This is called on startup
    """
    global ICONPNG
    ICONPNG = tk.PhotoImage("photo", file=ICONPNG_PATH)

    global FAVICON
    favicon_path = os.path.join(ASSETS_FOLDER, "favicon.ico")
    if platform.system() == "Linux":
        """
        .ico file cannot be used as an icon file in Linux. 
        It needs to be opened from PIL instead.
        """
        im = Image.open(favicon_path)
        FAVICON = ImageTk.PhotoImage(im)
    else:
        FAVICON = tk.PhotoImage("favicon", file=favicon_path)
