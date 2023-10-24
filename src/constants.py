import os
import sys
import tkinter as tk

# from platform import system
#
# platformD = system()

# https://stackoverflow.com/questions/22472124/what-is-sys-meipass-in-python
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Running from a compiled executable
    ASSETS_FOLDER = os.path.join(sys._MEIPASS, "resources", "assets")
else:
    ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), "..", "resources", "assets")

# if platformD == "Darwin":
#     FAVICON_PATH = os.path.join(ASSETS_FOLDER, "favicon.icns")
# elif platformD == "Windows":
#     FAVICON_PATH = os.path.join(ASSETS_FOLDER, "favicon.ico")
# else:
#     raise NotImplementedError

ICONPNG_PATH = os.path.join(ASSETS_FOLDER, "favicon-32x32.png")

ICONPNG = None


def load_images():
    global ICONPNG
    ICONPNG = tk.PhotoImage("photo", file=ICONPNG_PATH)
