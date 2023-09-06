import tkinter as tk

import ttkbootstrap as tb


class ToolBar(tb.Frame):
    def __init__(self, parent):
        tb.Frame.__init__(self, parent, width=50, bootstyle="medium")
        self.grid(
            column=0,
            row=0,
            sticky="w" + "e" + "n" + "s",
        )

        # Toolbar - Hand/Move Button
        img_hand = tk.PhotoImage(file="./data/resources/hand.png")
        button_hand = tb.Button(self, image=img_hand)
        button_hand.image = img_hand
        button_hand.grid(row=0, column=0, padx=10, pady=10)

        # Toolbar - Line Annotation Button
        img_line = tk.PhotoImage(file="./data/resources/line.png")
        button_line = tb.Button(self, image=img_line)
        button_line.image = img_line
        button_line.grid(row=2, column=0, padx=10, pady=10)

        # Toolbar - Squaure Annotation Button
        img_square = tk.PhotoImage(file="./data/resources/square.png")
        button_square = tb.Button(self, image=img_square)
        button_square.image = img_square
        button_square.grid(row=4, column=0, padx=10, pady=10)

        # Toolbar - Typing Button
        img_type = tk.PhotoImage(file="./data/resources/type.png")
        button_type = tb.Button(self, image=img_type)
        button_type.image = img_type
        button_type.grid(row=6, column=0, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    toolbar = ToolBar(root)
    root.mainloop()
