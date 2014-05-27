import unittest
from mock import patch, Mock
import sys

from contrib.bind.zone import Zone


class TestZone(unittest.TestCase):

    def test_dictionary(self):
        z = Zone()
        self.assertTrue(hasattr(z, 'contents'))

    def test_a_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.a(), [])
        self.assertEqual(z.a(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_aaa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}
        self.assertEqual(z.aaaa(), [])
        self.assertEqual(z.aaaa(record),
                         [{'ttl': 300, 'addr': '10.0.0.1', 'alias': '@'}])

    def test_caa_getset(self):
        z = Zone()
        record = {'ttl': 300, 'priority': 0, 'issue': 'thawte.com'}
        self.assertEqual(z.caa(), [])
        self.assertEqual(z.caa(record),
                         [{'ttl': 300, 'priority': 0, 'issue': 'thawte.com'}])

    def test_cert_getset(self):
        z = Zone()
        record = {'ttl': 300, 'type': 1, 'key-tag': '12179',
                  'algorithm': 3, 'cert-crl': 'AQPSKmynfz'}
        self.assertEqual(z.cert(), [])
        self.assertEqual(z.cert(record),
                         [{'ttl': 300, 'type': 1, 'key-tag': '12179',
                           'algorithm': 3, 'cert-crl': 'AQPSKmynfz'}])

    def test_cname_getset(self):
        z = Zone()
        record = {'ttl': 300, 'addr': 'abc.foo.com', 'alias': 'd'}
        self.assertEqual(z.cname(), [])
        self.assertEqual(z.cname(record),
                         [{'ttl': 300, 'addr': 'abc.foo.com', 'alias': 'd'}])

    def test_ns_getset(self):
        z = Zone()
        record = {'owner-name': 'example.com.', 'addr': '10.0.0.1',
                  'alias': 'ns1.example.com'}
        self.assertEqual(z.ns(), [])
        self.assertEqual(z.ns(record),
                         [{'owner-name': 'example.com.', 'addr': '10.0.0.1',
                           'alias': 'ns1.example.com'}])

    def test_ptr_getset(self):
        z = Zone()
        record = {'ttl': 2, 'addr': 'joe.example.com'}
        self.assertEqual(z.ptr(), [])
        self.assertEqual(z.ptr(record),
                         [{'ttl': 2, 'addr': 'joe.example.com'}])

    def test_soa_getset(self):
        z = Zone()
        record = {'ttl': '@', 'addr': 'ns1.example.com.',
                  'alias': 'hostmaster.example.com', 'serial': '2003080800',
                  'refresh': '12h', 'update-retry': '15m', 'expiry': '3w',
                  'minimum': '3h'}
        self.assertEqual(z.soa(), [])
        self.assertEqual(z.soa(record),
                         [{'ttl': '@', 'addr': 'ns1.example.com.',
                           'alias': 'hostmaster.example.com',
                           'serial': '2003080800',
                           'refresh': '12h',
                           'update-retry': '15m',
                           'expiry': '3w',
                           'minimum': '3h'}])

    def test_spf_getset(self):
        z = Zone()
        record = {'addr': 'example.com.',
                  'txt': '"v=spf1 mx include:example.net -all"'}
        self.assertEqual(z.spf(), [])
        self.assertEqual(z.spf(record),
                         [{'addr': 'example.com.',
                           'txt': '"v=spf1 mx include:example.net -all"'}])

    def test_srv_getset(self):
        z = Zone()
        record = {'addr': '_ldap._tcp.example.com.',
                  'priority': 0,
                  'weight': 0, 'port': 389,
                  'target': 'old-slow-box.example.com'}
        self.assertEqual(z.srv(), [])
        self.assertEqual(z.srv(record),
                         [{'addr': '_ldap._tcp.example.com.',
                           'priority': 0,
                           'weight': 0,
                           'port': 389,
                           'target': 'old-slow-box.example.com'}])

    def test_txt_getset(self):
        z = Zone()
        record = {'alias': 'joe',
                  'txt': '"Located in a black hole" " somewhere"'}
        self.assertEqual(z.txt(), [])
        self.assertEqual(z.txt(record),
                         [{'alias': 'joe',
                           'txt': '"Located in a black hole" " somewhere"'}])
