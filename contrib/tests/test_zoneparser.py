import sys
import unittest
from mock import (
    patch,
    Mock,
)

from contrib.bind.zoneparser import ZoneParser
# from contrib.bind.zone import Zone


class TestZoneParser(unittest.TestCase):

    ez = """example.com.                                  86400 IN SOA      ns1.example.com. hostmaster.example.com. 2002022401 10800 15 604800 10800
example.com.                                  86400 IN NS       ns1.example.com.
example.com.                                  86400 IN NS       ns2.smokeyjoe.com.
example.com.                                  86400 IN MX       10 mail.another.com.
bill.example.com.                             86400 IN A        192.168.0.3
fred.example.com.                             86400 IN A        192.168.0.4
ftp.example.com.                              86400 IN CNAME    www.example.com.
ns1.example.com.                              86400 IN A        192.168.0.1
www.example.com.                              86400 IN A        192.168.0.2"""

    def test_validate_attributes(self):
        sample_config = {'type': 'A', 'ttl': '300', 'addr': '10.0.0.1',
                         'alias': 'gateway'}
        err_config = {'type': 'spaghetti'}
        zp = ZoneParser('example.com')

        with self.assertRaises(KeyError):
            zp.from_dict(err_config)

        #TODO work with sample config

    def test_init_loads_keys_from_zone_class(self):
        zp = ZoneParser('example.com')
        self.assertIn('caa', zp.implemented_records)

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file(self, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez.split('\n')
        zp = ZoneParser('example.com', '/etc/db.foo')
        self.assertTrue(len(zp.contents) == 9)
