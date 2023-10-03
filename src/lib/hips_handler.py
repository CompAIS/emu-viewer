from dataclasses import dataclass

import astropy.coordinates as coords
import hips

# Todo - Figure why scikit doesn't want to work
# scikit keeps throwing error "Big-endian buffer not supported on little-endian compiler"
# might be able to fix by installing scikit-image 0.15.0 but it doesn't want to install


@dataclass
class HipsSurvey:
    ra: float = 0.0
    dec: float = 0.0
    FOV: str = ""
    projection: str = ""
    survey: str = ""


def open_hips(hips_survey):
    geometry = hips.WCSGeometry.create(
        skydir=coords.SkyCoord(
            hips_survey.ra, hips_survey.dec, unit="deg", frame="icrs"
        ),
        width=1000,
        height=1000,
        fov=hips_survey.FOV + " deg",
        coordsys="icrs",
        projection=hips_survey.projection,
    )

    result = hips.make_sky_image(geometry, hips_survey.survey, "fits")

    return result.image
