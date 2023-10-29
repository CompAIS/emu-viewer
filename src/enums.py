from enum import Enum


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
    protocol for streaming / transferring tiles of .fits, .png, or .jpeg data (and potentially more).
    Thus, HiPs surveys are treated as one of the following supported data types.
    """

    FITS = "fits"
    PNG = "png"
    JPEG = "jpeg"

    @classmethod
    def from_str(cls, s: str):
        """From a string, get the corresponding DataType enum variant."""

        m = cls._value2member_map_.get(s)
        if m is None:
            raise ValueError("{s} is not a valid DataType")
        return m
