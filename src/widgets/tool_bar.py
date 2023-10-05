import tkinter as tk

from PIL import Image, ImageTk

from src.lib.event_handler import EventHandler

ASSETS_FOLDER = "./resources/assets"
BUTTON_PAD = 5
SIZE = 30
BUTTON_WIDTH = 40


def open_icon(file_name):
    image = Image.open(f"{ASSETS_FOLDER}/{file_name}")
    r1 = image.size[0] / SIZE
    r2 = image.size[1] / SIZE
    ratio = max(r1, r2)
    newsize = (int(image.size[0] / ratio), int(image.size[1] / ratio))
    image = image.resize(newsize, Image.NEAREST)
    return image


class ToolBar(tk.Frame):
    toggle_eh = EventHandler()
    hand_eh = EventHandler()
    line_eh = EventHandler()
    typing_eh = EventHandler()
    bin_eh = EventHandler()

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, width=SIZE)
        self.grid(column=0, row=0, sticky=tk.NSEW)
        self.rowconfigure((0, 1, 2, 3), weight=0, uniform="a")
        self.rowconfigure(4, weight=1, uniform="a")
        self.columnconfigure(0, weight=1)
        self.selected_button = None

        # Toolbar - Hand/Move Button
        img_hand = ImageTk.PhotoImage(open_icon("hand.png"))
        self.button_hand = tk.Button(
            self, image=img_hand, relief=tk.FLAT, bg="lightblue", width=BUTTON_WIDTH
        )
        self.button_hand.image = img_hand
        self.button_hand.grid(
            row=0, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )
        self.button_hand.bind("<Button-1>", self.toggle_hand_button_color)

        # Toolbar - draw Annotation Button
        img_line = ImageTk.PhotoImage(open_icon("line.png"))
        self.button_line = tk.Button(
            self, image=img_line, relief=tk.FLAT, bg="lightblue", width=BUTTON_WIDTH
        )
        self.button_line.image = img_line
        self.button_line.grid(
            row=1, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )
        self.button_line.bind("<Button-1>", self.toggle_line_button_color)

        # Toolbar - Typing Button
        img_type = ImageTk.PhotoImage(open_icon("type.png"))
        self.button_type = tk.Button(
            self, image=img_type, relief=tk.FLAT, bg="lightblue", width=BUTTON_WIDTH
        )
        self.button_type.image = img_type
        self.button_type.grid(
            row=2, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )
        self.button_type.bind("<Button-1>", self.toggle_typing_button_color)

        # Toolbar - Bin Button
        img_bin = ImageTk.PhotoImage(open_icon("bin.png"))
        self.button_bin = tk.Button(
            self, image=img_bin, relief=tk.FLAT, bg="lightblue", width=BUTTON_WIDTH
        )
        self.button_bin.image = img_bin
        self.button_bin.grid(
            row=3, column=0, padx=BUTTON_PAD, pady=BUTTON_PAD, sticky=tk.NSEW
        )
        self.button_bin.bind("<Button-1>", self.toggle_bin_button_color)

    # Toggle bin pressed to red
    def toggle_bin_button_color(self, event):
        if self.selected_button is not None:
            self.selected_button.configure(bg="lightblue")
        self.selected_button = self.button_bin
        self.button_bin.configure(bg="red")
        self.bin_eh.invoke()

    # Toggle buttons pressed to red
    def toggle_hand_button_color(self, event):
        if self.selected_button is not None:
            self.selected_button.configure(bg="lightblue")
        self.selected_button = self.button_hand
        self.button_hand.configure(bg="red")
        self.toggle = 0
        self.toggle_eh.invoke(0)

    def toggle_line_button_color(self, event):
        if self.selected_button is not None:
            self.selected_button.configure(bg="lightblue")
        self.selected_button = self.button_line
        self.button_line.configure(bg="red")
        self.toggle = 1
        self.toggle_eh.invoke(1)

    def toggle_typing_button_color(self, event):
        if self.selected_button is not None:
            self.selected_button.configure(bg="lightblue")
        self.selected_button = self.button_type
        self.button_type.configure(bg="red")
        self.toggle = 2
        self.toggle_eh.invoke(2)


if __name__ == "__main__":
    root = tk.Tk()
    toolbar = ToolBar(root)
    root.mainloop()
