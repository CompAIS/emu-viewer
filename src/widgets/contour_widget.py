from src.widgets.base_widget import BaseWidget


class ContourWidget(BaseWidget):
    label = "Contours"
    dropdown = True

    def __init__(self, root):
        BaseWidget.__init__(self, root)
