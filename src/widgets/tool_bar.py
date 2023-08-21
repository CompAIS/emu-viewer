import ttkbootstrap as tb


class ToolBar(tb.Frame):
    def __init__(self, parent):
        tb.Frame.__init__(self, parent, width=50, height=250, bootstyle="light")
        self.grid(
            column=0,
            row=0,
            sticky="w" + "e" + "n" + "s",
        )
