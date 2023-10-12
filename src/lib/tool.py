import os
import tkinter

import matplotlib as mpl
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Very janky fix to get custom images to display, not sure how to edit matplotlib cbook images
ASSETS_FOLDER = "../../../../../../resources/assets/"


class NavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, parent, pack):
        # Edit toolitems to add new actions to toolbar
        # format of new tool is:
        # (
        #   text, # the text of the button (often not visible to users)
        #   tooltip_text, # the tooltip shown on hover (where possible)
        #   image_file, # name of the image for the button (without the extension)
        #   name_of_function, # name of the method in NavigationToolbar to call
        # )

        self.toolitems = (
            ("Home", "Reset original view", "home", "home"),
            ("Back", "Back to previous view", "back", "back"),
            ("Forward", "Forward to next view", "forward", "forward"),
            (None, None, None, None),
            (
                "Pan",
                "Left button pans, Right button zooms\n"
                "x/y fixes axis, CTRL fixes aspect",
                "move",
                "pan",
            ),
            ("Zoom", "Zoom to rectangle\nx/y fixes axis", "zoom_to_rect", "zoom"),
            (None, None, None, None),
            # TODO PX12-118 revisit
            # (
            #     "Line",
            #     "Draw line on figure",
            #     f"{ASSETS_FOLDER}/line",
            #     "draw_line",
            # ),
            (None, None, None, None),
            ("Save", "Save the figure", "filesave", "save_figure"),
        )
        super().__init__(canvas, parent, pack_toolbar=pack)

    def draw_line(self):
        print("Line annotation")
        if not self.canvas.widgetlock.available(self):
            self.set_message("line tool unavailable")
            return
        if self.mode == "line_tool":
            print("Unlock")
            self.mode = ""
            self.canvas.widgetlock.release(self)
        else:
            print("Lock")
            self.mode = "line_tool"
            self.canvas.widgetlock(self)

    def save_figure(self, *args):
        """
        Mostly stolen from base class. Modified to fit our needs.
        """

        filetypes = self.canvas.get_supported_filetypes().copy()
        default_filetype = self.canvas.get_default_filetype()

        default_filetype_name = filetypes.pop(default_filetype)
        sorted_filetypes = [(default_filetype, default_filetype_name)] + sorted(
            filetypes.items()
        )
        tk_filetypes = [(name, "*.%s" % ext) for ext, name in sorted_filetypes]

        defaultextension = ""
        initialdir = os.path.expanduser(mpl.rcParams["savefig.directory"])
        initialfile = self.canvas.get_default_filename()
        fname = tkinter.filedialog.asksaveasfilename(
            master=self.canvas.get_tk_widget().master,
            title="Save the figure",
            filetypes=tk_filetypes,
            defaultextension=defaultextension,
            initialdir=initialdir,
            initialfile=initialfile,
        )

        if fname in ["", ()]:
            return
        if initialdir != "":
            mpl.rcParams["savefig.directory"] = os.path.dirname(str(fname))
        try:
            # Where our implementation changes things https://stackoverflow.com/questions/4325733/save-a-subplot-in-matplotlib
            fig = self.canvas.figure
            extent = (
                fig.axes[0]
                .get_window_extent()
                .transformed(fig.dpi_scale_trans.inverted())
            )
            print(extent)
            fig.savefig(fname, bbox_inches=extent)
        except Exception as e:
            tkinter.messagebox.showerror("Error saving file", str(e))
