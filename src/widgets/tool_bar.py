import tkinter as tk

import ttkbootstrap as tb
from PIL import Image, ImageTk

from src.constants import ASSETS_FOLDER

BUTTON_PAD = 5
SIZE = 30


def open_icon(file_name):
    image = Image.open(f"{ASSETS_FOLDER}/{file_name}")
    r1 = image.size[0] / SIZE
    r2 = image.size[1] / SIZE
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.NEAREST)
    return image


class ToolBar(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, width=SIZE, bootstyle="medium")
        self.grid(column=0, row=0, sticky=tk.NSEW)
        self.grid_propagate(True)
        self.rowconfigure((0, 1, 2, 3), weight=0, uniform="a")
        self.rowconfigure(4, weight=1, uniform="a")
        self.columnconfigure(0, weight=1)

        # Toolbar - Hand/Move Button
        img_hand = ImageTk.PhotoImage(open_icon("hand.png"))
        button_hand = tb.Button(self, image=img_hand)
        button_hand.image = img_hand
        button_hand.grid(
            row=0, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )

        # Toolbar - Line Annotation Button
        img_line = ImageTk.PhotoImage(open_icon("line.png"))
        button_line = tb.Button(self, image=img_line)
        button_line.image = img_line
        button_line.grid(
            row=1, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )

        # Toolbar - Squaure Annotation Button
        img_square = ImageTk.PhotoImage(open_icon("square.png"))
        button_square = tb.Button(self, image=img_square)
        button_square.image = img_square
        button_square.grid(
            row=2, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )

        # Toolbar - Typing Button
        img_type = ImageTk.PhotoImage(open_icon("type.png"))
        button_type = tb.Button(self, image=img_type)
        button_type.image = img_type
        button_type.grid(
            row=3, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )


if __name__ == "__main__":
    root = tk.Tk()
    toolbar = ToolBar(root)
    root.mainloop()
