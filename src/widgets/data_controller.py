import ttkbootstrap as tb


class DataController(tb.Frame):
    def __init__(self, parent, x, y):
        tb.Frame.__init__(self, parent, width=250, height=250, bootstyle="light")
        self.grid(column=x, row=y, sticky="ne")
