from unittest import TestCase, mock

from src.main import MainWindow
from src.widgets.menu_bar import MenuBar  # Adjust the import path accordingly


class MenuBarTest(TestCase):
    @mock.patch("src.widgets.menu_bar.filedialog.askopenfilename", return_value="")
    def test_open_empty(self, mock_askopenfilename):
        main_app = MainWindow()
        listener = mock.Mock()
        main_app.menu_controller.open_file.add(listener)

        # manually call open
        main_app.menu_controller.open()

        # should not be open
        listener.assert_not_called()

    @mock.patch(
        "src.widgets.menu_bar.filedialog.askopenfilename", return_value="some_file.fits"
    )
    def test_open_with_name(self, mock_askopenfilename):
        main_app = MainWindow()
        listener = mock.Mock()

        # override all existing listeners and add a custom one
        main_app.menu_controller.open_file.clear()
        main_app.menu_controller.open_file.add(listener)

        # manually call open
        main_app.menu_controller.open()

        # should have called the listeners
        listener.assert_called_once_with("some_file.fits")
