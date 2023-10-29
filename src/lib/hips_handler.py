from dataclasses import dataclass
from typing import Optional

import astropy.units as u
from astropy import wcs
from astropy.coordinates import Angle, Latitude, Longitude
from astroquery.hips2fits import hips2fits

from src.enums import DataType


@dataclass
class HipsSurvey:
    """Dataclass provides all options to open a selected survey"""

    ra: float = 0.0
    dec: float = 0.0
    FOV: float = 0.0
    projection: str = ""
    survey: str = ""
    data_type: Optional[DataType] = None


def open_hips(hips_survey: HipsSurvey, wcs: Optional[wcs.WCS] = None):
    """Opens a HiPs survey with specified options provided by the HipsSurvey dataclass, currently only supports opening
    a survey with the RA and DEC in degrees

    :param hips_survey: options for the survey
    :param wcs: optionally a wcs to open the hips from
    :return: a tuple of image_data (numpy array in shape float[][]) and fits header if applicable
    """
    print("Opening HiPs survey...")

    if wcs is None:
        result = hips2fits.query(
            hips=hips_survey.survey,
            width=2000,
            height=2000,
            ra=Longitude(hips_survey.ra * u.deg),
            dec=Latitude(hips_survey.dec * u.deg),
            fov=Angle(hips_survey.FOV * u.deg),
            projection=hips_survey.projection,
            get_query_payload=False,
            format=hips_survey.data_type.value,
        )
    else:
        result = hips2fits.query_with_wcs(
            hips=hips_survey.survey,
            wcs=wcs,
            get_query_payload=False,
            format=hips_survey.data_type.value,
        )

    print("Done downloading HiPs survey - close message box if still open")

    if hips_survey.data_type == DataType.FITS:
        hdu = result[0]

        # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
        return hdu.data.squeeze(), hdu.header

    return result, None
