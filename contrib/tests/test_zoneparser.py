import sys
import unittest
from mock import (
    patch,
    Mock,
)

from contrib.bind.zoneparser import ZoneParser
# from contrib.bind.zone import Zone


class TestZoneParser(unittest.TestCase):

    ez = """$TTL    86400 ; 24 hours could have been written as 24h or 1d
; $TTL used for all RRs without explicit TTL value
$ORIGIN example.com.
@  1D  IN  SOA ns1.example.com. hostmaster.example.com. (
                  2002022401 ; serial
                  3H ; refresh
                  15 ; retry
                  1w ; expire
                  3h ; minimum
                 )
       IN  NS     ns1.example.com. ; in the domain
       IN  NS     ns2.smokeyjoe.com. ; external to domain
       IN MX  10 mail.another.com. ; external mail provider
; server host definitions
ns1    IN A      192.168.0.1  ;name server definition
www    IN  A      192.168.0.2  ;web server definition
ftp    IN CNAME  www.example.com.  ;ftp server definition
; non server domain hosts
bill   IN  A      192.168.0.3
fred   IN  A      192.168.0.4 """

    def test_validate_attributes(self):
        sample_config = {'type': 'A', 'ttl': '300', 'addr': '10.0.0.1',
                         'alias': 'gateway'}
        err_config = {'type': 'spaghetti'}
        zp = ZoneParser()

        with self.assertRaises(KeyError):
            zp.from_dict(err_config)

        #TODO work with sample config

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file(self, mopen):
        zp = ZoneParser('/etc/db.foo')
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez.split('\n')
        print zp.contents
        self.assertIn('5', [])
