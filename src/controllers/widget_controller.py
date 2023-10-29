import importlib
from enum import Enum
from functools import partial

# reference to the main window to avoid circular imports, see register_main
_main_window = None
# map of the Widget enum to an instance of that widget
_open_widgets = {}


class Widget(Enum):
    """A widget that has a separate window. These are handled by the widget_controller.

    Each of the widget classes in this list has a `label` and `dropdown` class variable that
    tells the widget controller what to do with it.

    ```py
    class HipsSelectorWidget(BaseWidget):
        label = "Hips Survey Selector"
        dropdown = False
    ```

    In this case, the widget's title will be `label` and the `dropdown` value tells us whether
    or not to put it in the "Widgets" menu dropdown.
    """

    # Q: Ok, so what is this mess?
    # A: Look, I'm sorry
    # The problem here is if we were to use a direct reference to each of these widget classes,
    #   we would end up with circular dependency issues.
    # It would require each of those modules to initialise up until the point these classes were initialised
    #   (i.e. the entire module, essentially) so we can reference them
    # Unfortunately, we import this module from each of these modules
    # So, we lazy-import them - the `value` method will import them
    #   the first time something in the callgraph actually needs to retrieve
    #   that class, and then cache it and reference that cached imported module
    #   for every subsequent call, meaning we lose no performance
    # I threw up a little in my mouth did you
    RENDERER = ("src.widgets.renderer_widget", "RendererWidget")
    IMAGE_TABLE = ("src.widgets.image_table_widget", "ImageTableWidget")
    CONTOURS = ("src.widgets.contour_widget", "ContourWidget")
    CATALOGUE = ("src.widgets.catalogue_widget", "CatalogueWidget")
    STATISTICS = ("src.widgets.statistics_widget", "StatisticsWidget")

    HIPS_SELECT = ("src.widgets.hips_selector_widget", "HipsSelectorWidget")

    def __init__(self, module_path, class_name):
        self._value = None
        self.module_path = module_path
        self.class_name = class_name

    @property
    def value(self):
        if self._value is None:
            module = importlib.import_module(self.module_path)
            self._value = getattr(module, self.class_name)
        return self._value


def open_widget(widget: Widget):
    """Open a widget and bring focus to it. If the widget is already open, just bring focus to it.

    This will use an internal dictionary of widget classes to BaseWidgets (of
        subclasses of BaseWidgets) and ensure only one of each widget is
        open simultaneously.

    :param widget: the widget to open
    """
    global _main_window, _open_widgets

    if widget not in _open_widgets:
        try:
            _open_widgets[widget] = widget.value(_main_window)
        except Exception as e:
            print(e)
            return

        _open_widgets[widget].on_close_eh.add(partial(_cleanup_widget, widget))

    def _focus_window(window):
        window.wm_state("normal")
        window.focus_set()

    _open_widgets[widget].after(1, _focus_window(_open_widgets[widget]))


def _cleanup_widget(widget: Widget):
    """Cleanup the reference to the widget in the internal dictionary.

    Used internally to ensure we don't maintain a reference to the widget after
        it's deletion. The widget itself manages it's closure (See BaseWidget#close).

    :param widget: the widget to cleanup
    """
    if widget in _open_widgets:
        del _open_widgets[widget]


def get_widget(widget: Widget):
    """Get the open widget window if it is open. None otherwise.

    :param widget: the widget to get
    """
    return _open_widgets.get(widget)


def register_main(main):
    """Set a reference to the main window for image_controller to use.

    This is a weird hack, since we need to be able to set the main_image on the window,
    but we can't import main.py since main.py also imports this module. So it would be
    circular in nature.

    I don't have time to think of an alternative for this.

    :param MainWindow main: the instance of MainWindow
        I can't import this for the type for obvious reasons
    """
    global _main_window

    _main_window = main
