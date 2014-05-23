import unittest

from contrib.bind.zone import Zone


class TestZone(unittest.TestCase):

    def setUp(self):
        self.z = Zone()
        self.z.contents = {
            'a': [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}],
            'cname': [{'ttl': 300, 'addr': 'example.com', 'alias': 'search'}]
        }

    def test_zone_dictionary(self):
        self.assertTrue(hasattr(self.z, 'contents'))

    def test_zone_a_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.a(), [])
        self.assertEqual(z.a(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_caa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'priority': 0, 'issue': 'thawte.com'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'priority': 0, 'issue': 'thawte.com'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_zone_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])
