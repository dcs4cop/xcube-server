from tornado.testing import AsyncHTTPTestCase

from test.helpers import new_test_service_context
from xcube_server.app import new_application
# For usage of the tornado.testing.AsyncHTTPTestCase see http://www.tornadoweb.org/en/stable/testing.html
from xcube_server.defaults import API_PREFIX


class HandlersTest(AsyncHTTPTestCase):

    def get_app(self):
        application = new_application()
        application.service_context = new_test_service_context()
        return application

    def assertResponseOK(self, response):
        self.assertEqual(200, response.code, response.reason)
        self.assertEqual("OK", response.reason)

    def assertBadRequestResponse(self, response, expected_reason="Bad Request"):
        self.assertEqual(400, response.code)
        self.assertEqual(expected_reason, response.reason)

    def test_fetch_base(self):
        response = self.fetch(API_PREFIX + '/')
        self.assertResponseOK(response)

    def test_fetch_wmts_kvp_capabilities(self):
        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?SERVICE=WMTS'
                                           '&REQUEST=GetCapabilities')
        self.assertResponseOK(response)

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?service=WMTS'
                                           '&request=GetCapabilities')
        self.assertResponseOK(response)

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?Service=WMTS'
                                           '&Request=GetCapabilities')
        self.assertResponseOK(response)

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?REQUEST=GetCapabilities')
        self.assertBadRequestResponse(response, 'Missing query parameter "service"')

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?SERVICE=WMS'
                                           '&REQUEST=GetCapabilities')
        self.assertBadRequestResponse(response, 'Value for "service" parameter must be "WMTS"')

    def test_fetch_wmts_kvp_tile(self):
        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?Service=WMTS'
                                           '&Request=GetTile'
                                           '&Version=1.0.0'
                                           '&Format=image/png'
                                           '&Style=Default'
                                           '&Layer=demo.conc_chl'
                                           '&TileMatrixSet=TileGrid_2000_1000'
                                           '&TileMatrix=0'
                                           '&TileRow=0'
                                           '&TileCol=0')
        self.assertResponseOK(response)

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?Service=WMTS'
                                           '&Request=GetTile'
                                           '&Version=1.0.0'
                                           '&Format=image/jpg'
                                           '&Style=Default'
                                           '&Layer=demo.conc_chl'
                                           '&TileMatrixSet=TileGrid_2000_1000'
                                           '&TileMatrix=0'
                                           '&TileRow=0'
                                           '&TileCol=0')
        self.assertBadRequestResponse(response, 'Value for "format" parameter must be "image/png"')

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?Service=WMTS'
                                           '&Request=GetTile'
                                           '&Version=1.1.0'
                                           '&Format=image/png'
                                           '&Style=Default'
                                           '&Layer=demo.conc_chl'
                                           '&TileMatrixSet=TileGrid_2000_1000'
                                           '&TileMatrix=0'
                                           '&TileRow=0'
                                           '&TileCol=0')
        self.assertBadRequestResponse(response, 'Value for "version" parameter must be "1.0.0"')

        response = self.fetch(API_PREFIX + '/wmts/1.0.0/kvp'
                                           '?Service=WMTS'
                                           '&Request=GetTile'
                                           '&Version=1.0.0'
                                           '&Format=image/png'
                                           '&Style=Default'
                                           '&Layer=conc_chl'
                                           '&TileMatrixSet=TileGrid_2000_1000'
                                           '&TileMatrix=0'
                                           '&TileRow=0'
                                           '&TileCol=0')
        self.assertBadRequestResponse(response, 'Value for "layer" parameter must be "<dataset>.<variable>"')

    def test_fetch_wmts_capabilities(self):
        response = self.fetch(API_PREFIX + '/wmts/1.0.0/WMTSCapabilities.xml')
        self.assertResponseOK(response)

    def test_fetch_wmts_tile(self):
        response = self.fetch(API_PREFIX + '/wmts/1.0.0/tile/demo/conc_chl/0/0/0.png')
        self.assertResponseOK(response)

    def test_fetch_wmts_tile_with_params(self):
        response = self.fetch(API_PREFIX + '/wmts/1.0.0/tile/demo/conc_chl/0/0/0.png?time=current&cbar=jet')
        self.assertResponseOK(response)

    def test_fetch_dataset_tile(self):
        response = self.fetch(API_PREFIX + '/tile/demo/conc_chl/0/0/0.png')
        self.assertResponseOK(response)

    def test_fetch_dataset_tile_with_params(self):
        response = self.fetch(API_PREFIX + '/tile/demo/conc_chl/0/0/0.png?time=current&cbar=jet')
        self.assertResponseOK(response)

    def test_fetch_dataset_tile_grid_ol4_json(self):
        response = self.fetch(API_PREFIX + '/tilegrid/demo/conc_chl/ol4')
        self.assertResponseOK(response)

    def test_fetch_dataset_tile_grid_cesium_json(self):
        response = self.fetch(API_PREFIX + '/tilegrid/demo/conc_chl/cesium')
        self.assertResponseOK(response)

    def test_fetch_ne2_tile(self):
        response = self.fetch(API_PREFIX + '/tile/ne2/0/0/0.jpg')
        self.assertResponseOK(response)

    def test_fetch_ne2_tile_grid(self):
        response = self.fetch(API_PREFIX + '/tilegrid/ne2/ol4')
        self.assertResponseOK(response)

    def test_fetch_datasets_json(self):
        response = self.fetch(API_PREFIX + '/datasets')
        self.assertResponseOK(response)

    def test_fetch_variables_json(self):
        response = self.fetch(API_PREFIX + '/variables/demo')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/variables/demo?client=ol4')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/variables/demo?client=cesium')
        self.assertResponseOK(response)

    def test_fetch_coords_json(self):
        response = self.fetch(API_PREFIX + '/coords/demo/time')
        self.assertResponseOK(response)

    def test_fetch_color_bars_json(self):
        response = self.fetch(API_PREFIX + '/colorbars')
        self.assertResponseOK(response)

    def test_fetch_color_bars_html(self):
        response = self.fetch(API_PREFIX + '/colorbars.html')
        self.assertResponseOK(response)

    def test_fetch_features(self):
        response = self.fetch(API_PREFIX + '/features/all?bbox=10,10,20,20')
        self.assertResponseOK(response)

    def test_fetch_features_for_dataset(self):
        response = self.fetch(API_PREFIX + '/features/all/demo')
        self.assertResponseOK(response)

    def test_fetch_time_series_info(self):
        response = self.fetch(API_PREFIX + '/ts')
        self.assertResponseOK(response)

    def test_fetch_time_series_point(self):
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/point')
        self.assertBadRequestResponse(response, 'Missing query parameter "lon"')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/point?lon=2.1')
        self.assertBadRequestResponse(response, 'Missing query parameter "lat"')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/point?lon=120.5&lat=-12.4')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/point?lon=2.1&lat=51.1')
        self.assertResponseOK(response)

    def test_fetch_time_series_geometry(self):
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometry', method="POST",
                              body='')
        self.assertBadRequestResponse(response, 'Invalid or missing GeoJSON geometry in request body')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometry', method="POST",
                              body='{"type":"Point"}')
        self.assertBadRequestResponse(response, 'Invalid GeoJSON geometry')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometry', method="POST",
                              body='{"type": "Point", "coordinates": [1, 51]}')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometry', method="POST",
                              body='{"type":"Polygon", "coordinates": [[[1, 51], [2, 51], [2, 52], [1, 51]]]}')
        self.assertResponseOK(response)

    def test_fetch_time_series_geometries(self):
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometries', method="POST",
                              body='')
        self.assertBadRequestResponse(response, 'Invalid or missing GeoJSON geometry collection in request body')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometries', method="POST",
                              body='{"type":"Point"}')
        self.assertBadRequestResponse(response, 'Invalid GeoJSON geometry collection')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometries', method="POST",
                              body='{"type": "GeometryCollection", "geometries": null}')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometries', method="POST",
                              body='{"type": "GeometryCollection", "geometries": []}')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/geometries', method="POST",
                              body='{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [1, 51]}]}')
        self.assertResponseOK(response)

    def test_fetch_time_series_features(self):
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/features', method="POST",
                              body='')
        self.assertBadRequestResponse(response, 'Invalid or missing GeoJSON feature collection in request body')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/features', method="POST",
                              body='{"type":"Point"}')
        self.assertBadRequestResponse(response, 'Invalid GeoJSON feature collection')
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/features', method="POST",
                              body='{"type": "FeatureCollection", "features": null}')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/features', method="POST",
                              body='{"type": "FeatureCollection", "features": []}')
        self.assertResponseOK(response)
        response = self.fetch(API_PREFIX + '/ts/demo/conc_chl/features', method="POST",
                              body='{"type": "FeatureCollection", "features": ['
                                   '  {"type": "Feature", "properties": {}, '
                                   '   "geometry": {"type": "Point", "coordinates": [1, 51]}}'
                                   ']}')
        self.assertResponseOK(response)
