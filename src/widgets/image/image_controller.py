import os
from multiprocessing.pool import ThreadPool
from tkinter import messagebox
from typing import TYPE_CHECKING, Optional, Tuple

import ttkbootstrap.dialogs as dialogs
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits
from numpy import typing as npt

from src.enums import DataType, Matching
from src.lib.event_handler import EventHandler
from src.lib.util import index_default
from src.widgets.hips_survey_selector import hips_handler
from src.widgets.image import fits_handler, image_frame, png_handler
from src.widgets.image.image_standalone_toplevel import StandaloneImage

if TYPE_CHECKING:
    from src.main import MainWindow

CLOSE_CONFIRM = "Are you sure you want to close all currently open images? Changes will not be saved."

# reference to the main window to avoid circular imports, see register_main
_main_window: Optional["MainWindow"] = None
_standalone_windows = []

_selected_image = None

selected_image_eh = EventHandler()
update_image_list_eh = EventHandler()


def get_selected_image() -> Optional[image_frame.ImageFrame]:
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


def set_selected_image(image: Optional[image_frame.ImageFrame]):
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


def get_images() -> list[image_frame.ImageFrame]:
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


def get_images_matched_to(match: Matching) -> list[image_frame.ImageFrame]:
    """Get the images matched to a certain Matching.

    Wrapper function to get_images which filters open images on whether
    or not they are matched to `match`.

    :return: the images matched to the given Matching
    """
    return [i for i in get_images() if i.is_matched(match)]


def get_coord_matched_limits(
    default: image_frame.ImageFrame,
) -> Tuple[SkyCoord, SkyCoord]:
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


def _open_image(
    image_data: npt.ArrayLike,
    image_data_header: Optional[fits.Header],
    file_name: str,
    data_type: DataType,
    from_hips: bool = False,
):
    """Open a new image with an ImageFrame.

    Internal function intended to only be called from wrapper functions open_fits, open_hips, and open_png.

    :param image_data: numpy array with the image's data (fits image or png image). Note that this should
        be float[][].
    :param image_data_header: HDU header for the .fits file. None for png/jpg.
    :param file_name: the name of the file where the data came from. HiPs survey name for hips
    :param data_type: The type of the data in image_data.
    :param from_hips: if the data came from a HiPs survey
    """
    global _main_window, _standalone_windows, update_image_list_eh

    if _main_window.main_image is None:
        # open to main window if nothing is currently open there
        _main_window.main_image = image_frame.ImageFrame(
            _main_window.main_image_container,
            _main_window,
            image_data,
            image_data_header,
            file_name,
            data_type,
            from_hips,
        )
        set_selected_image(_main_window.main_image)
    else:
        # otherwise open up a new top-level image
        new_window = StandaloneImage(
            _main_window, image_data, image_data_header, file_name, data_type, from_hips
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
    image_data, image_data_header = fits_handler.open_fits_file(file_path)
    file_name = os.path.basename(file_path)
    _open_image(image_data, image_data_header, file_name, DataType.FITS)


def open_png(file_path: str):
    """Open a .png file from a file path with an ImageFrame.

    :param str file_path: Path to the .fits file to open.
    """
    image_data = png_handler.open_png_file(file_path)
    file_name = os.path.basename(file_path)
    _open_image(image_data, None, file_name, DataType.PNG)


def open_hips(
    box_parent,
    hips_survey: hips_handler.HipsSurvey,
    image_wcs: Optional[wcs.WCS] = None,
):
    """Open a HiPs survey from a survey name, and optionally a WCS.

    Will download the survey at once with the given configuration and convert it to it's
    underlying type. This is currently slow, but unfortunately the best we have.

    Note that the surveys must be contactable by the
    [hips2fits](https://astroquery.readthedocs.io/en/latest/hips2fits/hips2fits.html) service. The list of valid survey
    names is available [here](https://aladin.cds.unistra.fr/hips/list).

    :param box_parent: a tk widget to own the message box which appears
    :param hips_survey: the hips survey to open with the respective information about where to open it
    :param Optional[wcs.WCS] image_wcs: a WCS to open the survey at
    """

    # so the message box doesn't block the downloading of the survey
    # i imagine that could be quite frustrating
    pool = ThreadPool(processes=1)
    r = pool.apply_async(hips_handler.open_hips, (hips_survey, image_wcs))

    dialogs.Messagebox.show_info(
        "Attempting to download HiPs survey - close this box so image can open once done",
        parent=box_parent,
        title="Download",
        alert=False,
    )

    image_data, image_header = r.get()

    _open_image(
        image_data, image_header, hips_survey.survey, hips_survey.data_type, True
    )


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
