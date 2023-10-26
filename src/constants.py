import os
import sys
import tkinter as tk

# https://stackoverflow.com/questions/22472124/what-is-sys-meipass-in-python
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running from a compiled executable
    ASSETS_FOLDER = os.path.join(sys._MEIPASS, "resources", "assets")
else:
    ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "resources", "assets")

ICONPNG_PATH = os.path.join(ASSETS_FOLDER, "favicon-32x32.png")
ICONPNG = None

FAVICON_PATH = os.path.join(ASSETS_FOLDER, "favicon.ico")


def load_images():
    """
    Load images once we have tk available. This is called on startup
    """
    global ICONPNG
    ICONPNG = tk.PhotoImage("photo", file=ICONPNG_PATH)
