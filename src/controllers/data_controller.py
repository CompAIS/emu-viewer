import ttkbootstrap as tb


class DataController(tb.Frame):
    def __init__(self, parent, root, w, h):
        tb.Frame.__init__(self, parent, width=w, height=h, bootstyle="dark")
