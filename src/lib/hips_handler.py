from dataclasses import dataclass

import astropy.units as u
from astropy.coordinates import Angle, Latitude, Longitude
from astroquery.hips2fits import hips2fits


@dataclass
class HipsSurvey:
    ra: float = 0.0
    dec: float = 0.0
    FOV: float = 0.0
    projection: str = ""
    survey: str = ""
    image_type: str = ""


def open_hips(hips_survey):
    result = hips2fits.query(
        hips=hips_survey.survey,
        width=2000,
        height=2000,
        ra=Longitude(hips_survey.ra * u.deg),
        dec=Latitude(hips_survey.dec * u.deg),
        fov=Angle(hips_survey.FOV * u.deg),
        projection=hips_survey.projection,
        get_query_payload=False,
        format=hips_survey.image_type,
    )

    if hips_survey.image_type == "fits":
        hdu = result[0]

        # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
        return hdu.data.squeeze(), hdu.header

    return result, None


def open_hips_with_wcs(hips_survey, wcs):
    result = hips2fits.query_with_wcs(
        hips=hips_survey.survey,
        wcs=wcs,
        get_query_payload=False,
        format=hips_survey.image_type,
    )

    if hips_survey.image_type == "fits":
        hdu = result[0]

        # some files have (1, 1, x, y) or (x, y, 1, 1) shape so we use .squeeze
        image_data = hdu.data.squeeze()
        image_header = hdu.header
    else:
        image_data = result
        image_header = None

    return image_data, image_header
