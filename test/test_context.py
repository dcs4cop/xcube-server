import unittest

import xarray as xr

from test.helpers import new_test_service_context
from xcube_server.errors import ServiceResourceNotFoundError


class ServiceContextTest(unittest.TestCase):
    def test_config_and_dataset_cache(self):
        ctx = new_test_service_context()
        self.assertNotIn('demo', ctx.dataset_cache)

        ctx.get_dataset('demo')
        self.assertIn('demo', ctx.dataset_cache)

        ctx.config = dict(Datasets=[
            dict(Identifier='demo',
                 Path="../../../xcube_server/res/demo/cube.nc"),
            dict(Identifier='demo2',
                 Path="../../../xcube_server/res/demo/cube.nc"),
        ])
        self.assertIn('demo', ctx.dataset_cache)
        self.assertNotIn('demo2', ctx.dataset_cache)

        ctx.get_dataset('demo2')
        self.assertIn('demo', ctx.dataset_cache)
        self.assertIn('demo2', ctx.dataset_cache)

        ctx.config = dict(Datasets=[
            dict(Identifier='demo2',
                 Path="../../../xcube_server/res/demo/cube.nc"),
        ])
        self.assertNotIn('demo', ctx.dataset_cache)
        self.assertIn('demo2', ctx.dataset_cache)

        ctx.config = dict()
        self.assertNotIn('demo', ctx.dataset_cache)
        self.assertNotIn('demo2', ctx.dataset_cache)

    def test_get_dataset_and_variable(self):
        ctx = new_test_service_context()
        ds, var = ctx.get_dataset_and_variable('demo', 'conc_tsm')
        self.assertIsInstance(ds, xr.Dataset)
        self.assertIsInstance(var, xr.DataArray)

        with self.assertRaises(ServiceResourceNotFoundError) as cm:
            ctx.get_dataset_and_variable('demox', 'conc_ys')
        self.assertEqual(404, cm.exception.status_code)
        self.assertEqual('Dataset "demox" not found', cm.exception.reason)

        with self.assertRaises(ServiceResourceNotFoundError) as cm:
            ctx.get_dataset_and_variable('demo', 'conc_ys')
        self.assertEqual(404, cm.exception.status_code)
        self.assertEqual('Variable "conc_ys" not found in dataset "demo"', cm.exception.reason)

    def test_get_color_mapping(self):
        ctx = new_test_service_context()
        cm = ctx.get_color_mapping('demo', 'conc_chl')
        self.assertEqual(('plasma', 0., 24.), cm)
        cm = ctx.get_color_mapping('demo', 'conc_tsm')
        self.assertEqual(('PuBuGn', 0., 100.), cm)
        cm = ctx.get_color_mapping('demo', 'kd489')
        self.assertEqual(('jet', 0., 6.), cm)
        cm = ctx.get_color_mapping('demo', '_')
        self.assertEqual(('jet', 0., 1.), cm)

    def test_get_feature_collections(self):
        ctx = new_test_service_context()
        feature_collections = ctx.get_place_groups()
        self.assertIsInstance(feature_collections, list)
        self.assertEqual([{'id': 'inside-cube', 'title': 'Points inside the cube'},
                          {'id': 'outside-cube', 'title': 'Points outside the cube'}],
                         feature_collections)

    def test_get_place_group(self):
        ctx = new_test_service_context()
        place_group = ctx.get_place_group()
        self.assertIsInstance(place_group, dict)
        self.assertIn("type", place_group)
        self.assertEqual("FeatureCollection", place_group["type"])
        self.assertIn("features", place_group)
        self.assertIsInstance(place_group["features"], list)
        self.assertEqual(6, len(place_group["features"]))
        self.assertIs(place_group, ctx.get_place_group())
        self.assertEqual([str(i) for i in range(6)],
                         [f["id"] for f in place_group["features"] if "id" in f])

    def test_get_place_group_by_name(self):
        ctx = new_test_service_context()
        place_group = ctx.get_place_group(place_group_id="inside-cube")
        self.assertIsInstance(place_group, dict)
        self.assertIn("type", place_group)
        self.assertEqual("FeatureCollection", place_group["type"])
        self.assertIn("features", place_group)
        self.assertIsInstance(place_group["features"], list)
        self.assertEqual(3, len(place_group["features"]))
        self.assertIs(place_group, ctx.get_place_group(place_group_id="inside-cube"))
        self.assertIsNot(place_group, ctx.get_place_group(place_group_id="outside-cube"))

        with self.assertRaises(ServiceResourceNotFoundError) as cm:
            ctx.get_place_group(place_group_id="bibo")
        self.assertEqual('HTTP 404: Place group "bibo" not found', f"{cm.exception}")
