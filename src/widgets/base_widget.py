import tkinter as tk
from functools import partial

from src.lib.event_handler import EventHandler


class BaseWidget(tk.Toplevel):
    # These need to be overriden on any class that extends this
    # Yes I know it's jank. Leave me alone!!!!!
    label = None
    dropdown = None

    def __init__(self, root):
        tk.Toplevel.__init__(self, root)
        self.root = root

        if self.__class__.label is None or self.__class__.dropdown is None:
            raise NotImplementedError(
                f"Both label and dropdown need to be set on the extending class! {self.__class__}"
            )

        self.title(self.__class__.label)
        self.resizable(False, False)

        self.on_close_eh = EventHandler()

        self.protocol(
            "WM_DELETE_WINDOW",
            partial(self.close),
        )

    def close(self):
        self.on_close_eh.invoke()
        self.destroy()
