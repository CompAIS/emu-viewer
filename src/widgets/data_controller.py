import ttkbootstrap as tb


class DataController(tb.Frame):
    def __init__(self, parent, x, y, cs, rs, w, h):
        tb.Frame.__init__(self, parent, width=w, height=h, bootstyle="light")
        self.grid(
            column=x,
            row=y,
            sticky="w" + "e" + "n" + "s",
            padx=10,
            pady=10,
            columnspan=cs,
            rowspan=rs,
        )
