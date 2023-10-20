import tkinter as tk

import ttkbootstrap as tb


class TableWidget(tb.Frame):
    def __init__(self, parent, headers, *args, **kwargs):
        super().__init__(parent, borderwidth=2, relief="solid", *args, **kwargs)

        self.grid_rowconfigure(0, weight=1, uniform="r")
        self.grid_columnconfigure(
            tuple([col for col in range(len(headers))]), weight=1, uniform="c"
        )

        self.rows = []

        for col, header in enumerate(headers):
            f = tb.Frame(self, bootstyle="dark")
            f.grid(row=0, column=col, sticky=tk.NSEW, ipadx=10, ipady=10)
            f.grid_rowconfigure(0, weight=1)
            f.grid_columnconfigure(0, weight=1)
            label = tb.Label(f, text=header, anchor=tk.CENTER)
            label.grid(row=0, column=0, sticky=tk.NSEW)

    def add_row(self, *row):
        i = len(self.rows)
        self.grid_rowconfigure(i + 1, weight=1, uniform="r")
        for col, cell in enumerate(row):
            cell.grid(row=len(self.rows) + i + 1, column=col, sticky=tk.NSEW)

            # frame = tb.Frame(self)
            # frame.grid(row=len(self.rows) + i, column=col, sticky=tk.NSEW)

        self.rows.append(row)

    def clear_rows(self):
        for row in self.rows:
            for cell in row:
                cell.destroy()

        self.rows = []


if __name__ == "__main__":
    window = tb.Window(themename="superhero")
    window.title("test")

    test = TableWidget(
        window, ("Image Num", "Image Name", "Matching"), bootstyle="dark"
    )
    test.grid(row=0, column=0, sticky=tk.NSEW, padx=50, pady=50)

    button1 = tb.Button(test, text="boo1")
    button2 = tb.Button(test, text="boo2")
    button3 = tb.Button(test, text="boo3")

    test.add_row((button1, button2, button3))

    def add_to_table_test():
        button_frame = tb.Frame(test, height=0)
        button_frame.grid_rowconfigure(0, weight=1, uniform="a")
        button_frame.grid_columnconfigure((0, 1), weight=1, uniform="a")

        buttonXY = tb.Button(button_frame, text="XY")
        buttonXY.grid(row=0, column=0)
        buttonR = tb.Button(button_frame, text="R")
        buttonR.grid(row=0, column=1)

        test.add_row(
            tb.Label(test, text=f"Image"),
            tb.Label(test, text=f"Image"),
            button_frame,
        )

    add = tb.Button(window, text="Add row", command=add_to_table_test)
    add.grid(row=1, column=1)

    window.mainloop()
