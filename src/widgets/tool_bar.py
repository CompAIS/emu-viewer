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

        img = tk.PhotoImage(file="./src/assets/zoom.png")

        button1 = tb.Button(self, image=img)
        button1.image = img
        button1.grid(row=0, column=0, padx=0, pady=0)


if __name__ == "__main__":
    root = tk.Tk()
    toolbar = ToolBar(root)
    root.mainloop()
