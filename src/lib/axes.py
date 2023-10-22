import numpy as np
from vispy.scene.widgets import AxisWidget
from vispy.visuals.axis import AxisVisual, Ticker, _get_ticks_talbot

from src.lib.fits_handler import pixel_to_coord

# override internals to force the ticks we want


class WCSAxisWidget(AxisWidget):
    # TODO xory is redundant given we have orientation
    def __init__(self, wcs, style, xory, orientation, **kwargs):
        super().__init__(orientation, **kwargs)
        if "tick_direction" not in kwargs:
            tickdir = {
                "left": (-1, 0),
                "right": (1, 0),
                "bottom": (0, 1),
                "top": (0, -1),
            }[orientation]
            kwargs["tick_direction"] = tickdir

        self.remove_subvisual(self.axis)
        self.axis = WCSAxisVisual(wcs, style, xory, **kwargs)
        self.add_subvisual(self.axis)


class WCSAxisVisual(AxisVisual):
    def __init__(self, wcs, style, xory, **kwargs):
        super().__init__(**kwargs)
        self.ticker = WCSTicker(self, wcs, style, xory)


class WCSTicker(Ticker):
    def __init__(self, axis, wcs, style, xory, tick_density=0.5, anchors=None):
        super().__init__(axis, anchors)
        self.axis = axis
        self.tick_density = tick_density
        self._anchors = anchors

        self.wcs = wcs
        self.style = style
        self.xory = xory

    def get_update(self):
        (
            major_tick_fractions,
            minor_tick_fractions,
            tick_labels,
        ) = self._get_tick_frac_labels()
        tick_pos, tick_label_pos, axis_label_pos, anchors = self._get_tick_positions(
            major_tick_fractions, minor_tick_fractions
        )
        return tick_pos, tick_labels, tick_label_pos, anchors, axis_label_pos

    def _get_tick_positions(self, major_tick_fractions, minor_tick_fractions):
        # tick direction is defined in visual coords, but use document
        # coords to determine the tick length
        trs = self.axis.transforms
        visual_to_document = trs.get_transform("visual", "document")
        direction = np.array(self.axis.tick_direction)
        direction /= np.linalg.norm(direction)

        if self._anchors is None:
            # use the document (pixel) coord system to set text anchors
            anchors = []
            if direction[0] < 0:
                anchors.append("right")
            elif direction[0] > 0:
                anchors.append("left")
            else:
                anchors.append("center")
            if direction[1] < 0:
                anchors.append("bottom")
            elif direction[1] > 0:
                anchors.append("top")
            else:
                anchors.append("middle")
        else:
            anchors = self._anchors

        # now figure out the tick positions in visual (data) coords
        doc_unit = visual_to_document.map([[0, 0], direction[:2]])
        doc_unit = doc_unit[1] - doc_unit[0]
        doc_len = np.linalg.norm(doc_unit)

        vectors = np.array(
            [
                [0.0, 0.0],
                direction * self.axis.minor_tick_length / doc_len,
                direction * self.axis.major_tick_length / doc_len,
                direction
                * (self.axis.major_tick_length + self.axis.tick_label_margin)
                / doc_len,
            ],
            dtype=float,
        )
        minor_vector = vectors[1] - vectors[0]
        major_vector = vectors[2] - vectors[0]
        label_vector = vectors[3] - vectors[0]

        axislabel_vector = (
            direction
            * (self.axis.major_tick_length + self.axis.axis_label_margin)
            / doc_len
        )

        major_origins, major_endpoints = self._tile_ticks(
            major_tick_fractions, major_vector
        )

        minor_origins, minor_endpoints = self._tile_ticks(
            minor_tick_fractions, minor_vector
        )

        tick_label_pos = major_origins + label_vector

        axis_label_pos = 0.5 * (self.axis.pos[0] + self.axis.pos[1]) + axislabel_vector

        num_major = len(major_tick_fractions)
        num_minor = len(minor_tick_fractions)

        c = np.empty([(num_major + num_minor) * 2, 2])

        c[0 : (num_major - 1) * 2 + 1 : 2] = major_origins
        c[1 : (num_major - 1) * 2 + 2 : 2] = major_endpoints
        c[(num_major - 1) * 2 + 2 :: 2] = minor_origins
        c[(num_major - 1) * 2 + 3 :: 2] = minor_endpoints

        return c, tick_label_pos, axis_label_pos, anchors

    def _tile_ticks(self, frac, tickvec):
        """Tiles tick marks along the axis."""
        origins = np.tile(self.axis._vec, (len(frac), 1))
        origins = self.axis.pos[0].T + (origins.T * frac).T
        endpoints = tickvec + origins
        return origins, endpoints

    def _get_tick_frac_labels(self):
        """Get the major ticks, minor ticks, and major labels"""
        minor_num = 4  # number of minor ticks per major division
        if self.axis.scale_type == "linear":
            domain = self.axis.domain
            if domain[1] < domain[0]:
                flip = True
                domain = domain[::-1]
            else:
                flip = False
            offset = domain[0]
            scale = domain[1] - domain[0]

            transforms = self.axis.transforms
            length = self.axis.pos[1] - self.axis.pos[0]  # in logical coords
            n_inches = np.sqrt(np.sum(length**2)) / transforms.dpi

            # !!!! this is where we (emu people) override self.tick_density
            major = _get_ticks_talbot(domain[0], domain[1], n_inches, self.tick_density)

            # !!! changing how labels are rendered
            labels = [pixel_to_coord(self.wcs, self.style, self.xory, x) for x in major]
            majstep = major[1] - major[0]
            minor = []
            minstep = majstep / (minor_num + 1)
            minstart = 0 if self.axis._stop_at_major[0] else -1
            minstop = -1 if self.axis._stop_at_major[1] else 0
            for i in range(minstart, len(major) + minstop):
                maj = major[0] + i * majstep
                minor.extend(
                    np.linspace(maj + minstep, maj + majstep - minstep, minor_num)
                )
            major_frac = major - offset
            minor_frac = np.array(minor) - offset
            if scale != 0:  # maybe something better to do here?
                major_frac /= scale
                minor_frac /= scale
            use_mask = (major_frac > -0.0001) & (major_frac < 1.0001)
            major_frac = major_frac[use_mask]
            labels = [l for li, l in enumerate(labels) if use_mask[li]]
            minor_frac = minor_frac[(minor_frac > -0.0001) & (minor_frac < 1.0001)]
            # Flip ticks coordinates if necessary :
            if flip:
                major_frac = 1 - major_frac
                minor_frac = 1 - minor_frac
        elif self.axis.scale_type == "logarithmic":
            return NotImplementedError
        elif self.axis.scale_type == "power":
            return NotImplementedError
        return major_frac, minor_frac, labels
