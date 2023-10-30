from enum import Enum
from typing import TYPE_CHECKING, Type

from astropy.visualization import (
    LinearStretch,
    LogStretch,
    ManualInterval,
    PowerStretch,
    SqrtStretch,
)

if TYPE_CHECKING:
    import numpy.typing as npt
    from astropy.visualization import BaseStretch


class Matching(Enum):
    """The type of matching across images.

    COORD represents co-ordinate matching / locking - panning on one image
        will cause all other COORD matched images to pan to the same co-ordinates.

    RENDER represents render matching. The render configuration of one
        image will cause all other RENDER matched images to have the same matching.

    ANNOTATION represents annotation matching. This is unimplemented (!!), but
        could represent annotations on one image matching across to other matched
        images.
    """

    COORD = "XY"
    RENDER = "R"
    ANNOTATION = "A"


class DataType(Enum):
    """The type of data from an image.

    Intended to be referenced with an image_data, so we know how to process that data.
    Note that HiPs is not an option - HiPs is not a separate file format, rather a
    protocol for streaming / transferring tiles of .fits, .png, or .jpg data (and potentially more).
    Thus, HiPs surveys are treated as one of the following supported data types.
    """

    FITS = "fits"
    PNG = "png"
    JPG = "jpg"

    @classmethod
    def from_str(cls, s: str):
        """From a string, get the corresponding DataType enum variant."""

        m = cls._value2member_map_.get(s)
        if m is None:
            raise ValueError(f"{s} is not a valid DataType")
        return m


class Scaling(Enum):
    """Represents a scaling / stretch to be done to data"""

    LINEAR = "Linear", LinearStretch
    LOG = "Log", LogStretch
    SQRT = "Sqrt", SqrtStretch
    SQUARED = "Squared", PowerStretch, 2

    def __init__(self, label: str, stretch_class: Type["BaseStretch"], *stretch_args):
        self.label = label
        self.stretch_class = stretch_class
        self.stretch_args = stretch_args

    @classmethod
    def from_str(cls, s: str):
        """From a string, get the corresponding Scaling enum variant."""

        for member in cls:
            if member.label == s:
                return member

        raise ValueError(f"{s} is not a valid Scaling")

    @property
    def value(self):
        return self.label

    def stretch(
        self, image_data: "npt.ArrayLike", vmin: float, vmax: float
    ) -> "npt.ArrayLike":
        """Stretches the given data according to the scaling.

        :param image_data: the data to stretch
        :param vmin: the minimum value - anything below will be clipped
        :param vmax: the maximum value - anything above will be clipped
        """
        return (self.stretch_class(*self.stretch_args) + ManualInterval(vmin, vmax))(
            image_data
        )
