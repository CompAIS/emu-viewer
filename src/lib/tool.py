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

    def update_stack(self):
        self.push_current()
