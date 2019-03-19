import unittest

import numpy as np
import shapely.geometry
import xarray as xr

from xcube_server.utils import get_dataset_geometry, get_dataset_bounds, get_geometry_mask, \
    timestamp_to_iso_string


class TimestampToIsoStringTest(unittest.TestCase):
    def test_it_with_default_res(self):
        self.assertEqual("2018-09-05T00:00:00Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05")))
        self.assertEqual("2018-09-05T10:35:42Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05 10:35:42")))
        self.assertEqual("2018-09-05T10:35:42Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05 10:35:42.164")))

    def test_it_with_h_res(self):
        self.assertEqual("2018-09-05T00:00:00Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05"), freq="H"))
        self.assertEqual("2018-09-05T11:00:00Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05 10:35:42"), freq="H"))
        self.assertEqual("2018-09-05T11:00:00Z",
                         timestamp_to_iso_string(np.datetime64("2018-09-05 10:35:42.164"), freq="H"))


class GetDatasetGeometryTest(unittest.TestCase):

    def test_nominal(self):
        ds1, ds2 = _get_nominal_datasets()
        bounds = get_dataset_geometry(ds1)
        self.assertEqual(shapely.geometry.box(-25.0, -15.0, 15.0, 15.0), bounds)
        bounds = get_dataset_geometry(ds2)
        self.assertEqual(shapely.geometry.box(-25.0, -15.0, 15.0, 15.0), bounds)

    def test_antimeridian(self):
        ds1, ds2 = _get_antimeridian_datasets()
        bounds = get_dataset_geometry(ds1)
        self.assertEqual(shapely.geometry.MultiPolygon(
            polygons=[
                shapely.geometry.box(165.0, -15.0, 180.0, 15.0),
                shapely.geometry.box(-180.0, -15.0, -155.0, 15.0)
            ]),
            bounds)
        bounds = get_dataset_geometry(ds2)
        self.assertEqual(shapely.geometry.MultiPolygon(
            polygons=[
                shapely.geometry.box(165.0, -15.0, 180.0, 15.0),
                shapely.geometry.box(-180.0, -15.0, -155.0, 15.0)
            ]),
            bounds)


class GetDatasetBoundsTest(unittest.TestCase):
    def test_nominal(self):
        ds1, ds2 = _get_nominal_datasets()
        bounds = get_dataset_bounds(ds1)
        self.assertEqual((-25.0, -15.0, 15.0, 15.0), bounds)
        bounds = get_dataset_bounds(ds2)
        self.assertEqual((-25.0, -15.0, 15.0, 15.0), bounds)

    def test_anti_meridian(self):
        ds1, ds2 = _get_antimeridian_datasets()
        bounds = get_dataset_bounds(ds1)
        self.assertEqual((165.0, -15.0, -155.0, 15.0), bounds)
        bounds = get_dataset_bounds(ds2)
        self.assertEqual((165.0, -15.0, -155.0, 15.0), bounds)


def _get_nominal_datasets():
    data_vars = dict(a=(("time", "lat", "lon"), np.random.rand(5, 3, 4)))

    coords = dict(time=(("time",), np.array(range(0, 5))),
                  lat=(("lat",), np.array([-10, 0., 10])),
                  lon=(("lon",), np.array([-20, -10, 0., 10])))
    ds1 = xr.Dataset(coords=coords, data_vars=data_vars)

    coords.update(dict(lat_bnds=(("lat", "bnds"), np.array([[-15, -5], [-5., 5], [5, 15]])),
                       lon_bnds=(
                           ("lon", "bnds"), np.array([[-25., -15.], [-15., -5.], [-5., 5.], [5., 15.]]))
                       ))
    ds2 = xr.Dataset(coords=coords, data_vars=data_vars)

    return ds1, ds2


def _get_antimeridian_datasets():
    ds1, ds2 = _get_nominal_datasets()
    ds1 = ds1.assign_coords(lon=(("lon",), np.array([170., 180., -170., -160.])))
    ds2 = ds2.assign_coords(
        lon_bnds=(("lon", 2), np.array([[165., 175], [175., -175.], [-175., -165], [-165., -155.]])))
    return ds1, ds2


class GetGeometryMaskTest(unittest.TestCase):
    def test_get_geometry_mask(self):
        w = 16
        h = 8
        res = 1.0
        lon_min = 0
        lat_min = 0
        lon_max = lon_min + w * res
        lat_max = lat_min + h * res

        triangle = shapely.geometry.Polygon(((lon_min, lat_min), (lon_max, lat_min), (lon_max, lat_max),
                                             (lon_min, lat_min)))

        actual_mask = get_geometry_mask(w, h, triangle, lon_min, lat_min, res)
        expected_mask = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                                  [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                  [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=np.byte)
        np.testing.assert_array_almost_equal(expected_mask, actual_mask.astype('byte'))

        smaller_triangle = triangle.buffer(-1.5 * res)
        actual_mask = get_geometry_mask(w, h, smaller_triangle, lon_min, lat_min, res)
        expected_mask = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.byte)
        np.testing.assert_array_almost_equal(expected_mask, actual_mask)
