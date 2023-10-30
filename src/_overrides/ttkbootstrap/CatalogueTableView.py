from tkinter import ttk

from ttkbootstrap.constants import *
from ttkbootstrap.localization import MessageCatalog
from ttkbootstrap.tableview import TableCellRightClickMenu, Tableview

# Note from us before you go into the depths below.
#
# We did this for the following reasons:
# - Removed all functions of resetting hidden columns
# -----


class CatalogueTableView(Tableview):
    def __init(self, master, coldata, rowdata, paginated, searchable, bootstyle):
        super().__init__(
            master=master,
            coldata=coldata,
            rowdata=rowdata,
            paginated=paginated,
            searchable=searchable,
            bootstyle=bootstyle,
        )

    def _build_pagination_frame(self):
        """Build the frame containing the pagination widgets. This
        frame is only built if `pagination=True` when creating the
        widget.
        """
        pageframe = ttk.Frame(self)
        pageframe.pack(fill=X, anchor=N)

        # Removed reset button from the pagination frame

        ttk.Button(
            master=pageframe,
            text="»",
            command=self.goto_last_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)
        ttk.Button(
            master=pageframe,
            text="›",
            command=self.goto_next_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Button(
            master=pageframe,
            text="‹",
            command=self.goto_prev_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)
        ttk.Button(
            master=pageframe,
            text="«",
            command=self.goto_first_page,
            style="symbol.Link.TButton",
        ).pack(side=RIGHT, fill=Y)

        ttk.Separator(pageframe, orient=VERTICAL).pack(side=RIGHT, padx=10)

        lbl = ttk.Label(pageframe, textvariable=self._pagelimit)
        lbl.pack(side=RIGHT, padx=(0, 5))
        ttk.Label(pageframe, text=MessageCatalog.translate("of")).pack(
            side=RIGHT, padx=(5, 0)
        )

        index = ttk.Entry(pageframe, textvariable=self._pageindex, width=4)
        index.pack(side=RIGHT)
        index.bind("<Return>", self.goto_page, "+")
        index.bind("<KP_Enter>", self.goto_page, "+")

        ttk.Label(pageframe, text=MessageCatalog.translate("Page")).pack(
            side=RIGHT, padx=5
        )

    def _build_tableview_widget(self, coldata, rowdata, bootstyle):
        """Build the data table"""
        if self._searchable:
            self._build_search_frame()

        self.view = ttk.Treeview(
            master=self,
            columns=[x for x in range(len(coldata))],
            height=self._height,
            selectmode=EXTENDED,
            show=HEADINGS,
            bootstyle=f"{bootstyle}-table",
        )
        self.view.pack(fill=BOTH, expand=YES, side=TOP)
        self.hbar = ttk.Scrollbar(
            master=self, command=self.view.xview, orient=HORIZONTAL
        )
        self.hbar.pack(fill=X)
        self.view.configure(xscrollcommand=self.hbar.set)

        if self._paginated:
            self._build_pagination_frame()

        self.build_table_data(coldata, rowdata)

        self._rightclickmenu_cell = TableCellRightClickMenu(self)
        self._set_widget_binding()

    def reset_table(self):
        pass
