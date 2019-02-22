import re
import unittest

from xcube_server import service
from xcube_server.service import parse_tile_cache_config


class TileCacheConfigTest(unittest.TestCase):
    def test_parse_tile_cache_config(self):
        self.assertEqual({'no_cache': True}, parse_tile_cache_config(""))
        self.assertEqual({'no_cache': True}, parse_tile_cache_config("0"))
        self.assertEqual({'no_cache': True}, parse_tile_cache_config("0M"))
        self.assertEqual({'no_cache': True}, parse_tile_cache_config("off"))
        self.assertEqual({'no_cache': True}, parse_tile_cache_config("OFF"))
        self.assertEqual({'capacity': 200001}, parse_tile_cache_config("200001"))
        self.assertEqual({'capacity': 200001}, parse_tile_cache_config("200001B"))
        self.assertEqual({'capacity': 300000}, parse_tile_cache_config("300K"))
        self.assertEqual({'capacity': 3000000}, parse_tile_cache_config("3M"))
        self.assertEqual({'capacity': 7000000}, parse_tile_cache_config("7m"))
        self.assertEqual({'capacity': 2000000000}, parse_tile_cache_config("2g"))
        self.assertEqual({'capacity': 2000000000}, parse_tile_cache_config("2G"))
        self.assertEqual({'capacity': 1000000000000}, parse_tile_cache_config("1T"))

        with self.assertRaises(ValueError) as cm:
            parse_tile_cache_config("7n")
        self.assertEqual("invalid tile cache size: '7N'", f"{cm.exception}")

        with self.assertRaises(ValueError) as cm:
            parse_tile_cache_config("-2g")
        self.assertEqual("negative tile cache size: '-2G'", f"{cm.exception}")


class UrlPatternTest(unittest.TestCase):
    def test_url_pattern_works(self):
        re_pattern = service.url_pattern('/open/{{id1}}ws/{{id2}}wf')
        matcher = re.fullmatch(re_pattern, '/open/34ws/a66wf')
        self.assertIsNotNone(matcher)
        self.assertEqual(matcher.groupdict(), {'id1': '34', 'id2': 'a66'})

        re_pattern = service.url_pattern('/open/ws{{id1}}/wf{{id2}}')
        matcher = re.fullmatch(re_pattern, '/open/ws34/wfa66')
        self.assertIsNotNone(matcher)
        self.assertEqual(matcher.groupdict(), {'id1': '34', 'id2': 'a66'})

        x = 'C%3A%5CUsers%5CNorman%5CIdeaProjects%5Cccitools%5Cect-core%5Ctest%5Cui%5CTEST_WS_3'
        re_pattern = service.url_pattern('/ws/{{base_dir}}/res/{{res_name}}/add')
        matcher = re.fullmatch(re_pattern, '/ws/%s/res/SST/add' % x)
        self.assertIsNotNone(matcher)
        self.assertEqual(matcher.groupdict(), {'base_dir': x, 'res_name': 'SST'})

    def test_url_pattern_ok(self):
        self.assertEqual(service.url_pattern('/version'),
                         '/version')
        self.assertEqual(service.url_pattern('{{num}}/get'),
                         '(?P<num>[^\;\/\?\:\@\&\=\+\$\,]+)/get')
        self.assertEqual(service.url_pattern('/open/{{ws_name}}'),
                         '/open/(?P<ws_name>[^\;\/\?\:\@\&\=\+\$\,]+)')
        self.assertEqual(service.url_pattern('/open/ws{{id1}}/wf{{id2}}'),
                         '/open/ws(?P<id1>[^\;\/\?\:\@\&\=\+\$\,]+)/wf(?P<id2>[^\;\/\?\:\@\&\=\+\$\,]+)')

    def test_url_pattern_fail(self):
        with self.assertRaises(ValueError) as cm:
            service.url_pattern('/open/{{ws/name}}')
        self.assertEqual(str(cm.exception), 'name in {{name}} must be a valid identifier, but got "ws/name"')

        with self.assertRaises(ValueError) as cm:
            service.url_pattern('/info/{{id}')
        self.assertEqual(str(cm.exception), 'no matching "}}" after "{{" in "/info/{{id}"')
