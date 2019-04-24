# The MIT License (MIT)
# Copyright (c) 2018 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import functools
from typing import Optional, Any, Tuple

from .geoextent import GeoExtent

__author__ = "Norman Fomferra (Brockmann Consult GmbH)"

MODE_LE = -1
MODE_EQ = 0
MODE_GE = 1


class TileGrid:
    """
    Image pyramid tile grid.

    :param num_levels: Number of pyramid levels.
    :param num_level_zero_tiles_x: Number of tiles at level zero in X direction.
    :param num_level_zero_tiles_y:  Number of tiles at level zero in Y direction.
    :param tile_width: The tile width.
    :param tile_height: The tile height.
    :param geo_extent: The geographical extent.
    """

    def __init__(self,
                 num_levels: int,
                 num_level_zero_tiles_x: int,
                 num_level_zero_tiles_y: int,
                 tile_width: int,
                 tile_height: int,
                 geo_extent: GeoExtent):
        self.num_levels = num_levels
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.num_level_zero_tiles_x = num_level_zero_tiles_x
        self.num_level_zero_tiles_y = num_level_zero_tiles_y
        self.geo_extent = geo_extent

    def num_tiles(self, level: int) -> Tuple[int, int]:
        return self.num_tiles_x(level), self.num_tiles_y(level)

    def num_tiles_x(self, level: int) -> int:
        return self.num_level_zero_tiles_x * (1 << level)

    def num_tiles_y(self, level: int) -> int:
        return self.num_level_zero_tiles_y * (1 << level)

    def size(self, level: int) -> Tuple[int, int]:
        return self.width(level), self.height(level)

    def width(self, level: int) -> int:
        return self.num_tiles_x(level) * self.tile_width

    def height(self, level: int) -> int:
        return self.num_tiles_y(level) * self.tile_height

    @property
    def tile_size(self) -> Tuple[int, int]:
        return self.tile_width, self.tile_height

    @property
    def min_width(self) -> int:
        return self.width(0)

    @property
    def min_height(self) -> int:
        return self.height(0)

    @property
    def max_width(self) -> int:
        return self.width(self.num_levels - 1)

    @property
    def max_height(self) -> int:
        return self.height(self.num_levels - 1)

    def __hash__(self) -> int:
        return self.num_levels \
               + 2 * self.tile_width \
               + 4 * self.tile_height \
               + 8 * self.num_level_zero_tiles_x \
               + 16 * self.num_level_zero_tiles_y \
               + hash(self.geo_extent)  # noqa: E126

    def __eq__(self, o: Any) -> bool:
        try:
            return self.num_levels == o.num_levels \
                   and self.tile_width == o.tile_width \
                   and self.tile_height == o.tile_height \
                   and self.num_level_zero_tiles_x == o.num_level_zero_tiles_x \
                   and self.num_level_zero_tiles_y == o.num_level_zero_tiles_y \
                   and self.geo_extent == o.geo_extent  # noqa: E126
        except AttributeError:
            return False

    def __str__(self):
        return '\n'.join(['number of pyramid levels: {nl}'.format(nl=self.num_levels),
                          'number of tiles at level zero: {nx} x {ny}'.format(nx=self.num_level_zero_tiles_x,
                                                                              ny=self.num_level_zero_tiles_y),
                          'pyramid tile size: {tw} x {th}'.format(tw=self.tile_width, th=self.tile_height),
                          'image size at level zero: {w} x {h}'.format(w=self.min_width, h=self.min_height),
                          'image size at level {k}: {w} x {h}'.format(k=self.num_levels - 1,
                                                                      w=self.max_width, h=self.max_height)])

    def __repr__(self):
        return 'TileGrid(%s, %s, %s, %s, %s, %s)' % (
            self.num_levels, self.num_level_zero_tiles_x, self.num_level_zero_tiles_y,
            self.tile_width, self.tile_height, repr(self.geo_extent))

    def to_json(self):
        return dict(numLevelZeroTilesX=self.num_level_zero_tiles_x,
                    numLevelZeroTilesY=self.num_level_zero_tiles_y,
                    tileWidth=self.tile_width,
                    tileHeight=self.tile_height,
                    numLevels=self.num_levels,
                    invY=self.geo_extent.inv_y,
                    extent=dict(west=self.geo_extent.west,
                                south=self.geo_extent.south,
                                east=self.geo_extent.east,
                                north=self.geo_extent.north))

    @classmethod
    def create(cls,
               w: int, h: int,
               tile_width: int, tile_height: int,
               geo_extent: GeoExtent) -> 'TileGrid':
        """
        Create a new TilingScheme object for image size given by *w* and *h*.

        *geo_spatial_rect* is a tuple (*x1*, *y1*, *x2*, *y2*) and is the geo-spatial rectangle
        that covers all grid cells and is extracted directly from the geo-location information
        in the (NetCDF/CF) file:
        * *x1* longitude of center of first row and first column in image;
        * *y1* latitude of center of first row and first column in image;
        * *x2* longitude of center of last row and last column in image;
        * *y2* latitude of center of last row and last column in image.

        Note that
        * *x1* may be greater than *x2* which means that the anti-meridian is crossed;
        * *y1* is usually greater than *y2* meaning that the latitude axis is flipped.

        :param w: original image width
        :param h: original image height
        :param tile_width: optimal tile width
        :param tile_height: optimal tile height
        :param geo_extent: The geo-spatial extent
        :return: A new TilingScheme object
        """
        gsb_x1, gsb_y1, gsb_x2, gsb_y2 = geo_extent.coords

        w_mode = MODE_GE
        if gsb_x1 == -180. and gsb_x2 == 180.:
            w_mode = MODE_EQ
        h_mode = MODE_GE
        if gsb_y1 == -90. and gsb_y1 == 90. or gsb_y1 == 90. and gsb_y2 == -90.:
            h_mode = MODE_EQ

        (w_new, h_new), (tw, th), (nt0x, nt0y), nl = pow2_2d_subdivision(w, h,
                                                                         w_mode=w_mode, h_mode=h_mode,
                                                                         tw_opt=min(w, tile_width or 256),
                                                                         th_opt=min(h, tile_height or 256))

        new_extent = cls.adjust_geo_extent(geo_extent, w, h, w_new, h_new)
        return TileGrid(nl, nt0x, nt0y, tw, th, new_extent)

    @classmethod
    def adjust_geo_extent(cls, geo_extent, w_old, h_old, w_new, h_new) -> GeoExtent:

        assert w_new >= w_old
        assert h_new >= h_old

        gsb_x1, gsb_y1, gsb_x2, gsb_y2 = geo_extent.coords

        if gsb_x1 < gsb_x2:
            # crossing_anti-meridian = False
            gsb_w = gsb_x2 - gsb_x1
        else:
            # crossing_anti-meridian = True
            gsb_w = 360. + gsb_x2 - gsb_x1
        gsb_h = gsb_y2 - gsb_y1

        if w_new > w_old:
            gsb_w_new = w_new * gsb_w / w_old
            # We cannot adjust gsb_x1, because we expect x to increase with x indices
            # and hence we would later on have to read from negative x indexes
            gsb_x2_new = gsb_x1 + gsb_w_new
            if gsb_x2_new > 180.:
                gsb_x2_new = gsb_x2_new - 360.
        else:
            gsb_x2_new = gsb_x2

        if h_new > h_old:
            gsb_h_new = h_new * gsb_h / h_old
            if geo_extent.inv_y:
                # We cannot adjust gsb_y2, because we expect y to decrease with y indices
                # and hence we would later on have to read from negative y indexes
                gsb_y2_new = gsb_y2
                gsb_y1_new = gsb_y2_new - gsb_h_new
            else:
                # We cannot adjust gsb_y1, because we expect y to increase with y indices
                # and hence we would later on have to read from negative y indexes
                gsb_y1_new = gsb_y1
                gsb_y2_new = gsb_y1_new + gsb_h_new
        else:
            gsb_y1_new, gsb_y2_new = gsb_y1, gsb_y2

        return GeoExtent(west=gsb_x1,
                         south=gsb_y1_new,
                         east=gsb_x2_new,
                         north=gsb_y2_new,
                         inv_y=geo_extent.inv_y,
                         eps=geo_extent.eps)


@functools.lru_cache(maxsize=256)
def pow2_2d_subdivision(w: int, h: int,
                        w_mode: int = MODE_EQ, h_mode: int = MODE_EQ,
                        tw_opt: Optional[int] = None, th_opt: Optional[int] = None,
                        tw_min: Optional[int] = None, th_min: Optional[int] = None,
                        tw_max: Optional[int] = None, th_max: Optional[int] = None,
                        nt0_max: Optional[int] = None,
                        nl_max: Optional[int] = None):
    """
    Get a pyramidal quad-tree subdivision of a 2D image rectangle given by image width *w* and height *h*.
    We want all pyramid levels to use the same tile size *tw*, *th*. All but the lowest resolution level, level zero,
    shall have 2 times the number of tiles of a previous level in both x- and y-direction.

    As there can be multiple of such subdivisions, we select an optimum subdivision by constraints. We want
    (in this order):
    1. the resolution of the highest pyramid level, *nl* - 1, to be as close as possible to *w*, *h*;
    2. the number of tiles in level zero to be as small as possible;
    3. the tile sizes *tw*, *th* to be as close as possible to *tw_opt*, *th_opt*, if given;
    4. a maximum number of levels.

    :param w: image width
    :param h: image height
    :param w_mode: optional mode for horizontal direction, -1: *w_act* <= *w*, 0: *w_act* == *w*, +1: *w_act* >= *w*
    :param h_mode: optional mode for vertical direction, -1: *h_act* <= *h*, 0: *h_act* == *h*, +1: *h_act* >= *h*
    :param tw_opt: optional optimum tile width
    :param th_opt: optional optimum tile height
    :param tw_min: optional minimum tile width
    :param th_min: optional minimum tile height
    :param tw_max: optional maximum tile width
    :param th_max: optional maximum tile height
    :param nt0_max: optional maximum number of tiles at level zero of pyramid
    :param nl_max: optional maximum number of pyramid levels
    :return: a tuple ((*w_act*, *h_act*), (*tw*, *th*), (*nt0_x*, *nt0_y*), *nl*) with
             *w_act*, *h_act* being the final image width and height in the pyramids's highest resolution level;
             *tw*, *th* being the tile width and height;
             *nt0_x*, *nt0_y* being the number of tiles at level zero of pyramid in horizontal and vertical direction;
             and *nl* being the total number of pyramid levels.
    """
    w_act, tw, nt0_x, nl_x = pow2_1d_subdivision(w, s_mode=w_mode,
                                                 ts_opt=tw_opt, ts_min=tw_min, ts_max=tw_max,
                                                 nt0_max=nt0_max, nl_max=nl_max)
    h_act, th, nt0_y, nl_y = pow2_1d_subdivision(h, s_mode=h_mode,
                                                 ts_opt=th_opt, ts_min=th_min, ts_max=th_max,
                                                 nt0_max=nt0_max, nl_max=nl_max)
    if nl_x < nl_y:
        nl = nl_x
        f = 1 << (nl - 1)
        h0 = (h_act + f - 1) // f
        nt0_y = (h0 + th - 1) // th
    elif nl_x > nl_y:
        nl = nl_y
        f = 1 << (nl - 1)
        w0 = (w_act + f - 1) // f
        nt0_x = (w0 + tw - 1) // tw
    else:
        nl = nl_x

    return (w_act, h_act), (tw, th), (nt0_x, nt0_y), nl


def pow2_1d_subdivision(s_act: int,
                        s_mode: int = MODE_EQ,
                        ts_opt: Optional[int] = None,
                        ts_min: Optional[int] = None,
                        ts_max: Optional[int] = None,
                        nt0_max: Optional[int] = None,
                        nl_max: Optional[int] = None):
    return pow2_1d_subdivisions(s_act,
                                s_mode=s_mode,
                                ts_opt=ts_opt,
                                ts_min=ts_min, ts_max=ts_max,
                                nt0_max=nt0_max, nl_max=nl_max)[0]


def pow2_1d_subdivisions(s: int,
                         s_mode: int = MODE_EQ,
                         ts_opt: Optional[int] = None,
                         ts_min: Optional[int] = None,
                         ts_max: Optional[int] = None,
                         nt0_max: Optional[int] = None,
                         nl_max: Optional[int] = None):
    if s is None or s < 1:
        raise ValueError('invalid s')

    if s == ts_opt:
        return [(s, s, 1, 1)]

    ts_min = ts_min or min(s, (ts_opt // 2 if ts_opt else 200))
    ts_max = ts_max or min(s, (ts_opt * 2 if ts_opt else 1200))
    nt0_max = nt0_max or 8
    nl_max = nl_max or 16

    if ts_min < 1:
        raise ValueError('invalid ts_min')
    if ts_max < 1:
        raise ValueError('invalid ts_max')
    if ts_opt is not None and ts_opt < 1:
        raise ValueError('invalid ts_opt')
    if nt0_max < 1:
        raise ValueError('invalid nt0_max')
    if nl_max < 1:
        raise ValueError('invalid nl_max')

    subdivisions = []
    for ts in range(ts_min, ts_max + 1):
        s_max_min = s if s_mode == MODE_EQ or s_mode == MODE_GE else s - (ts - 1)
        s_max_max = s if s_mode == MODE_EQ or s_mode == MODE_LE else s + (ts - 1)
        for nt0 in range(1, nt0_max):
            s_max = nt0 * ts
            if s_max > s_max_max:
                break
            for nl in range(2, nl_max):
                nt = (1 << (nl - 1)) * nt0
                s_max = nt * ts
                ok = False
                if s_mode == MODE_GE:
                    if s_max >= s:
                        if s_max > s_max_max:
                            break
                        ok = True
                elif s_mode == MODE_LE:
                    if s >= s_max >= s_max_min:
                        ok = True
                else:  # s_mode == MODE_EQ:
                    if s_max == s:
                        ok = True
                    elif s_max > s:
                        break
                if ok:
                    rec = s_max, ts, nt0, nl
                    subdivisions.append(rec)

    if not subdivisions:
        return [(s, s, 1, 1)]

    # maximize nl
    subdivisions.sort(key=lambda r: r[3], reverse=True)
    if ts_opt:
        # minimize |ts - ts_opt|
        subdivisions.sort(key=lambda r: abs(r[1] - ts_opt))
    # minimize nt0
    subdivisions.sort(key=lambda r: r[2])
    # minimize s_max - s_min
    subdivisions.sort(key=lambda r: r[0] - s)

    return subdivisions
