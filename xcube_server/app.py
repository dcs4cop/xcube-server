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

import os

from tornado.web import Application, StaticFileHandler

from xcube_server.defaults import DEFAULT_NAME, API_PREFIX
from xcube_server.handlers import GetNE2TileHandler, GetDatasetVarTileHandler, InfoHandler, GetNE2TileGridHandler, \
    GetDatasetVarTileGridHandler, GetWMTSCapabilitiesXmlHandler, GetColorBarsJsonHandler, GetColorBarsHtmlHandler, \
    GetDatasetsHandler, FindPlacesHandler, FindDatasetPlacesHandler, \
    GetDatasetCoordsHandler, GetTimeSeriesInfoHandler, GetTimeSeriesForPointHandler, WMTSKvpHandler, \
    GetTimeSeriesForGeometryHandler, GetTimeSeriesForFeaturesHandler, GetTimeSeriesForGeometriesHandler, \
    GetPlaceGroupsHandler, GetDatasetVarLegendHandler, GetDatasetHandler
from xcube_server.service import url_pattern

__author__ = "Norman Fomferra (Brockmann Consult GmbH)"


def new_application(name: str = DEFAULT_NAME):
    prefix = f"/{name}{API_PREFIX}"
    application = Application([
        (prefix + '/res/(.*)',
         StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'res')}),
        (prefix + url_pattern('/'),
         InfoHandler),

        (prefix + url_pattern('/wmts/1.0.0/WMTSCapabilities.xml'),
         GetWMTSCapabilitiesXmlHandler),
        (prefix + url_pattern('/wmts/1.0.0/tile/{{ds_id}}/{{var_name}}/{{z}}/{{y}}/{{x}}.png'),
         GetDatasetVarTileHandler),
        (prefix + url_pattern('/wmts/kvp'),
         WMTSKvpHandler),

        # Natural Earth 2 tiles for testing

        (prefix + url_pattern('/datasets'),
         GetDatasetsHandler),
        (prefix + url_pattern('/datasets/{{ds_id}}'),
         GetDatasetHandler),
        (prefix + url_pattern('/datasets/{{ds_id}}/coords/{{dim_name}}'),
         GetDatasetCoordsHandler),
        (prefix + url_pattern('/datasets/{{ds_id}}/vars/{{var_name}}/legend.png'),
         GetDatasetVarLegendHandler),
        (prefix + url_pattern('/datasets/{{ds_id}}/vars/{{var_name}}/tiles/{{z}}/{{x}}/{{y}}.png'),
         GetDatasetVarTileHandler),
        (prefix + url_pattern('/datasets/{{ds_id}}/vars/{{var_name}}/tilegrid'),
         GetDatasetVarTileGridHandler),

        # Natural Earth 2 tiles for testing

        (prefix + url_pattern('/ne2/tilegrid'),
         GetNE2TileGridHandler),
        (prefix + url_pattern('/ne2/tiles/{{z}}/{{x}}/{{y}}.jpg'),
         GetNE2TileHandler),

        # Color Bars API

        (prefix + url_pattern('/colorbars'),
         GetColorBarsJsonHandler),
        (prefix + url_pattern('/colorbars.html'),
         GetColorBarsHtmlHandler),

        # Places API (PRELIMINARY & UNSTABLE - will be revised soon)

        (prefix + url_pattern('/places'),
         GetPlaceGroupsHandler),
        (prefix + url_pattern('/places/{{collection_name}}'),
         FindPlacesHandler),
        (prefix + url_pattern('/places/{{collection_name}}/{{ds_id}}'),
         FindDatasetPlacesHandler),

        # Time-series API (for VITO's DCS4COP viewer only, PRELIMINARY & UNSTABLE - will be revised soon)

        (prefix + url_pattern('/ts'),
         GetTimeSeriesInfoHandler),
        (prefix + url_pattern('/ts/{{ds_id}}/{{var_name}}/point'),
         GetTimeSeriesForPointHandler),
        (prefix + url_pattern('/ts/{{ds_id}}/{{var_name}}/geometry'),
         GetTimeSeriesForGeometryHandler),
        (prefix + url_pattern('/ts/{{ds_id}}/{{var_name}}/geometries'),
         GetTimeSeriesForGeometriesHandler),
        (prefix + url_pattern('/ts/{{ds_id}}/{{var_name}}/places'),
         GetTimeSeriesForFeaturesHandler),
    ])
    return application
