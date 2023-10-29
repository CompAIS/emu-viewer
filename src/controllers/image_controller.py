import os
from tkinter import messagebox
from typing import List, Optional, Tuple

from astropy import wcs
from astropy.coordinates import SkyCoord
from numpy import typing as npt

# TODO figure out what to do with these handlers (and their casing)
import src.lib.fits_handler as Fits_handler
import src.lib.hips_handler as Hips_handler
import src.lib.png_handler as png_handler
from src.enums import DataType, Matching
from src.lib.event_handler import EventHandler
from src.lib.util import index_default
from src.widgets import image_widget as iw
from src.widgets.image_standalone_toplevel import StandaloneImage

CLOSE_CONFIRM = "Are you sure you want to close all currently open images? Changes will not be saved."

# reference to the main window to avoid circular imports, see register_main
_main_window = None
_standalone_windows = []

_selected_image = None

selected_image_eh = EventHandler()
update_image_list_eh = EventHandler()


def get_selected_image() -> Optional[iw.ImageFrame]:
    """Get currently selected image in program.

    The selected image is determined by whichever the last image to be focused was,
    or whichever image was selected in the image table.

    :return: the currently selected ImageFrame, or None
    """
    global _selected_image

    if _selected_image is None:
        # No image loaded so nothing to select
        return None

    if isinstance(_selected_image, StandaloneImage):
        return _selected_image.image_frame

    # otherwise it's just an ImageFrame directly
    return _selected_image


def set_selected_image(image: Optional[iw.ImageFrame]):
    """Set whichever image is currently "selected".

    Will invoke the event handler `selected_image_eh`.

    :param image: the image to set as selected. None is valid and passed
        on to consumers of the event, will act as "no images open".
    """
    global _selected_image

    if _selected_image == image:
        # Do nothing, return early to avoid the event handler invocation
        return

    _selected_image = image
    selected_image_eh.invoke(image)


def get_images() -> List[iw.ImageFrame]:
    """Get all the currently open ImageFrames.

    :return: a list of ImageFrames
    """
    global _main_window, _standalone_windows

    if _main_window.main_image is None:
        return []

    images = [_main_window.main_image]

    for w in _standalone_windows:
        # unwrap the image_frame from the windows
        images.append(w.image_frame)

    return images


# TODO check this Matching hint works correctly
def get_images_matched_to(match: Matching) -> List[iw.ImageFrame]:
    """Get the images matched to a certain Matching.

    Wrapper function to get_images which filters open images on whether
    or not they are matched to `match`.

    :return: the images matched to the given Matching
    """
    return [i for i in get_images() if i.is_matched(match)]


def get_coord_matched_limits(default: iw.ImageFrame) -> Tuple[SkyCoord, SkyCoord]:
    """Get the current limits of the images that are being coordinate-matched.

    If there are no images currently coordinate matched, use the provided default
    (this will be the limits of the image that is being co-ordinate matched).

    Wrapper to get_images_matched_to.

    :param default: the ImageFrame to get the limits from if no images are currently
        co-ordinate matched

    :return: tuple of limits for currently co-ordinate matched images, in the form
        (bottom left, top right)
    """

    # since all the images which are co-ordinate matched will have the same limits,
    # we can just grab the first one
    return index_default(get_images_matched_to(Matching.COORD), 0, default).limits


# TODO type image_data_header?
def _open_image(
    image_data: npt.ArrayLike, image_data_header, file_name: str, data_type: DataType
):
    """Open a new image with an ImageFrame.

    Internal function intended to only be called from wrapper functions open_fits, open_hips, and open_png.

    :param image_data: numpy array with the image's data (fits image or png image). Note that this should
        be float[][].
    :param image_data_header: HDU header for the .fits file. None for png/jpeg.
    :param file_name: the name of the file where the data came from. HiPs survey name for hips
    :param data_type: The type of the data in the file.
    """
    global _main_window, _standalone_windows, update_image_list_eh

    if _main_window.main_image is None:
        # open to main window if nothing is currently open there
        _main_window.main_image = iw.ImageFrame(
            _main_window.main_image_container,
            _main_window,
            image_data,
            image_data_header,
            file_name,
            data_type,
        )
        set_selected_image(_main_window.main_image)
    else:
        new_window = StandaloneImage(
            _main_window, image_data, image_data_header, file_name, data_type
        )
        _standalone_windows.append(new_window)
        set_selected_image(new_window.image_frame)

    # TODO this invoke is a bit weird
    update_image_list_eh.invoke(get_selected_image(), get_images())


def open_fits(file_path: str):
    """Open a .fits file from a file path with an ImageFrame.

    Note that (currently) it will always open the HDU at [0].

    :param file_path: Path to the .fits file to open.
    """
    image_data, image_data_header = Fits_handler.open_fits_file(file_path)
    file_name = os.path.basename(file_path)
    _open_image(image_data, image_data_header, file_name, DataType.FITS)


def open_png(file_path: str):
    """Open a .png file from a file path with an ImageFrame.

    :param str file_path: Path to the .fits file to open.
    """
    image_data = png_handler.open_png_file(file_path)
    file_name = os.path.basename(file_path)
    _open_image(image_data, None, file_name, DataType.PNG)


def open_hips(hips_survey: str, wcs: Optional[wcs.WCS] = None):
    """Open a HiPs survey from a survey name, and optionally a WCS.

    Will download the survey at once with the given configuration and convert it to it's
    underlying type. This is currently slow, but unfortunately the best we have.

    Note that the surveys must be contactable by the [hips2fits](https://astroquery.readthedocs.io/en/latest/hips2fits/hips2fits.html)
    service. The list of valid survey names is available [here](https://aladin.cds.unistra.fr/hips/list).

    :param str hips_survey: the name of the survey to open
    :param Optional[wcs.WCS] wcs: a WCS to open the survey at
    """
    # TODO this should probably be handled by the hips_handler (that's what it's there for!)
    if wcs is None:
        image_data, image_header = Hips_handler.open_hips(hips_survey)
    else:
        image_data, image_header = Hips_handler.open_hips_with_wcs(hips_survey, wcs)

    # TODO image_type here
    _open_image(image_data, image_header, hips_survey.survey, hips_survey.image_type)


def close_images():
    """Closes all currently open images, with a message box warning."""
    global _main_window, _standalone_windows, update_image_list_eh

    if get_selected_image() is not None and not messagebox.askyesno(
        title="Confirmation", message=CLOSE_CONFIRM
    ):
        return

    print("Closing all images...")

    # destroy all windows
    for window in _standalone_windows:
        window.destroy()

    _standalone_windows = []

    # destroy main image
    if _main_window.main_image is not None:
        _main_window.main_image.destroy()
        _main_window.main_image = None

    _main_window.update()

    set_selected_image(None)
    update_image_list_eh.invoke(None, [])


def close_standalone(window: StandaloneImage):
    """Close a single standalone image window.

    Will set focus to the main window and set the selected image to
    the main image.
    """
    global _main_window, _standalone_windows, update_image_list_eh

    # destroy the standalone
    window.destroy()
    _standalone_windows.remove(window)

    # focus the main window
    _main_window.after(1, lambda: _main_window.focus_set())

    # update selected images
    set_selected_image(_main_window.main_image)
    # TODO again this is weird
    update_image_list_eh.invoke(get_selected_image(), get_images())


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
