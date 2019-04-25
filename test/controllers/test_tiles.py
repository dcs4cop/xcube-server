import unittest

from test.helpers import new_test_service_context, RequestParamsMock
from xcube_server.context import ServiceContext
from xcube_server.controllers.tiles import get_dataset_tile, get_ne2_tile, get_dataset_tile_grid, get_ne2_tile_grid, \
    get_legend
from xcube_server.defaults import API_PREFIX
from xcube_server.errors import ServiceBadRequestError, ServiceResourceNotFoundError


class TilesControllerTest(unittest.TestCase):

    def test_get_dataset_tile(self):
        ctx = new_test_service_context()
        tile = get_dataset_tile(ctx, 'demo', 'conc_tsm', '0', '0', '0', RequestParamsMock())
        self.assertIsInstance(tile, bytes)

        tile = get_dataset_tile(ctx, 'demo', 'conc_tsm', '-20', '0', '0', RequestParamsMock())
        self.assertIsInstance(tile, bytes)

    def test_get_dataset_tile_with_all_params(self):
        ctx = new_test_service_context()
        tile = get_dataset_tile(ctx, 'demo', 'conc_tsm', '0', '0', '0', RequestParamsMock(time='current', cbar='plasma',
                                                                                          vmin='0.1', vmax='0.3'))
        self.assertIsInstance(tile, bytes)

    def test_get_dataset_tile_with_time_dim(self):
        ctx = new_test_service_context()
        tile = get_dataset_tile(ctx, 'demo', 'conc_tsm', '0', '0', '0', RequestParamsMock(time='2017-01-26'))
        self.assertIsInstance(tile, bytes)

        ctx = new_test_service_context()
        tile = get_dataset_tile(ctx, 'demo', 'conc_tsm', '0', '0', '0', RequestParamsMock(time='current'))
        self.assertIsInstance(tile, bytes)

        with self.assertRaises(ServiceBadRequestError) as cm:
            get_dataset_tile(ctx, 'demo', 'conc_tsm', '0', '0', '0', RequestParamsMock(time='Gnaaark!'))
        self.assertEqual(400, cm.exception.status_code)
        self.assertEqual("'Gnaaark!' is not a valid value for "
                         "dimension 'time' of variable 'conc_tsm' of dataset 'demo'",
                         cm.exception.reason)

    def test_get_ne2_tile(self):
        ctx = new_test_service_context()
        tile = get_ne2_tile(ctx, '0', '0', '0', RequestParamsMock())
        self.assertIsInstance(tile, bytes)

    def test_get_dataset_tile_grid(self):
        self.maxDiff = None

        ctx = new_test_service_context()
        tile_grid = get_dataset_tile_grid(ctx, 'demo', 'conc_chl', 'ol4', 'http://bibo')
        self.assertEqual({
            'url': self.base_url + '/datasets/demo/vars/conc_chl/tiles/{z}/{x}/{y}.png',
            'projection': 'EPSG:4326',
            'minZoom': 0,
            'maxZoom': 2,
            'tileGrid': {'extent': [0.0, 50.0, 5.0, 52.5],
                         'origin': [0.0, 52.5],
                         'resolutions': [0.01, 0.005, 0.0025],
                         'tileSize': [250, 250]},
        }, tile_grid)

        tile_grid = get_dataset_tile_grid(ctx, 'demo', 'conc_chl', 'cesium', 'http://bibo')
        self.assertEqual({
            'url': self.base_url + '/datasets/demo/vars/conc_chl/tiles/{z}/{x}/{y}.png',
            'rectangle': dict(west=0.0, south=50.0, east=5.0, north=52.5),
            'minimumLevel': 0,
            'maximumLevel': 2,
            'tileWidth': 250,
            'tileHeight': 250,
            'tilingScheme': {'rectangle': dict(west=0.0, south=50.0, east=5.0, north=52.5),
                             'numberOfLevelZeroTilesX': 2,
                             'numberOfLevelZeroTilesY': 1},
        }, tile_grid)

        with self.assertRaises(ServiceBadRequestError) as cm:
            get_dataset_tile_grid(ctx, 'demo', 'conc_chl', 'ol2.json', 'http://bibo')
        self.assertEqual(400, cm.exception.status_code)
        self.assertEqual('Unknown tile client "ol2.json"', cm.exception.reason)

    def test_get_legend(self):
        ctx = new_test_service_context()
        image = get_legend(ctx, 'demo', 'conc_chl', RequestParamsMock())
        self.assertEqual("<class 'bytes'>", str(type(image)))

        with self.assertRaises(ServiceResourceNotFoundError) as cm:
            get_legend(ctx, 'demo', 'conc_chl', RequestParamsMock(cbar='sun-shine'))
        self.assertEqual('color bar sun-shine not found', cm.exception.reason)

        with self.assertRaises(ServiceBadRequestError) as cm:
            get_legend(ctx, 'demo', 'conc_chl', RequestParamsMock(vmin='sun-shine'))
        self.assertEqual("""Parameter "vmin" must be a number, but was 'sun-shine'""", cm.exception.reason)

        with self.assertRaises(ServiceBadRequestError) as cm:
            get_legend(ctx, 'demo', 'conc_chl', RequestParamsMock(width='sun-shine'))
        self.assertEqual("""Parameter "width" must be an integer, but was 'sun-shine'""", cm.exception.reason)

    def test_get_ne2_tile_grid(self):
        ctx = ServiceContext()
        tile_grid = get_ne2_tile_grid(ctx, 'ol4', 'http://bibo')
        self.assertEqual({
            'url': self.base_url + '/ne2/tiles/{z}/{x}/{y}.jpg',
            'projection': 'EPSG:4326',
            'minZoom': 0,
            'maxZoom': 2,
            'tileGrid': {'extent': [-180.0, -90.0, 180.0, 90.0],
                         'origin': [-180.0, 90.0],
                         'resolutions': [0.703125, 0.3515625, 0.17578125],
                         'tileSize': [256, 256]},
        }, tile_grid)

        with self.assertRaises(ServiceBadRequestError) as cm:
            get_ne2_tile_grid(ctx, 'cesium', 'http://bibo')
        self.assertEqual(400, cm.exception.status_code)
        self.assertEqual("Unknown tile client 'cesium'", cm.exception.reason)

    @property
    def base_url(self):
        return f'http://bibo/xcube{API_PREFIX}'
