import astropy.coordinates as coords
import hips


def open_hips(hips_survey):
    geometry = hips.WCSGeometry.create(
        skydir=coords.SkyCoord(0, 0, unit="deg", frame="galactic"),
        width=1000,
        height=1000,
        fov="3 deg",
        coordsys="galactic",
        projection="AIT",
    )

    result = hips.make_sky_image(geometry, hips_survey, "fits")

    return result.image
