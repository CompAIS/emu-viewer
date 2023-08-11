import ttkbootstrap as ttk


class DataHandler(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent, bootstyle="success")
        self.grid(column=2, row=0)
