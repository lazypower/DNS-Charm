import sys
import unittest
from mock import (
    patch,
    Mock,
)

from contrib.bind.zoneparser import ZoneParser
# from contrib.bind.zone import Zone


class TestZoneParser(unittest.TestCase):

# Be cautious with your editor, this blob contains necessary tab characters.
    ez = """example.com. 				604800 IN 	SOA 	example.com. root.example.com. 2 604800 86400 2419200 604800
example.com. 				604800 IN 	NS 	ns.example.com.
example.com. 				604800 IN 	A 	192.168.1.10
example.com. 				604800 IN 	AAAA 	::1
ns.example.com. 				604800 IN 	A 	192.168.1.10
www.example.com. 				604800 IN 	CNAME 	foo.example.com."""

    def test_validate_attributes(self):
        sample_config = {'type': 'A', 'ttl': '300', 'addr': '10.0.0.1',
                         'alias': 'gateway'}
        err_config = {'type': 'spaghetti'}
        zp = ZoneParser('example.com')

        #TODO work with sample config

    def test_init_loads_keys_from_zone_class(self):
        zp = ZoneParser('example.com')
        self.assertIn('aaaa', zp.implemented_records)

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file(self, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez.split('\n')
        zp = ZoneParser('example.com', '/etc/db.foo')
        self.assertTrue(len(zp.contents) == 6)

    @patch('contrib.bind.zoneparser.ZoneParser.a_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.aaaa_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.cname_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.ns_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.soa_from_array')
    def test_array_to_zone(self, soam, nsm, cnm, aam, am):
        zp = ZoneParser('example.com')
        zcontents = self.ez.split('\n')
        zp.contents = zcontents
        zp.array_to_zone()
        soam.assert_called_with(zcontents[0].split('\t'))
        nsm.assert_called_with(zcontents[1].split('\t'))
        cnm.assert_called_with(zcontents[5].split('\t'))
        aam.assert_called_with(zcontents[3].split('\t'))
        am.assert_called_with(zcontents[4].split('\t'))

    def test_soa_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez.split('\n')
        zp.soa_from_array(zcontents[0].split('\t'))
        self.assertEqual(zp.zone.contents['soa'], [{'addr': 'example.com.',
                                                'alias': 'root.example.com.',
                                                'expiry': '2419200',
                                                'minimum': '604800',
                                                'refresh': '604800',
                                                'serial': '2',
                                                'ttl': '604800',
                                                'update-retry': '86400'}])

    def test_cname_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez.split('\n')
        zp.cname_from_array(zcontents[5].split('\t'))
        self.assertEqual(zp.zone.contents['cname'], [{'ttl': '604800', 
                                                    'alias': 'www',
                                                    'addr': 'foo.example.com.'}])

    def test_a_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez.split('\n')
        zp.a_from_array(zcontents[2].split('\t'))
        self.assertEqual(zp.zone.contents['a'], [{'ttl': '604800',
                                                  'addr': '192.168.1.10',
                                                  'alias': ''}])

    def test_aaaa_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez.split('\n')
        zp.aaaa_from_array(zcontents[3].split('\t'))
        self.assertEqual(zp.zone.contents['aaaa'], [{'ttl': '604800',
                                                    'addr': '::1',
                                                    'alias': ''}])

    @patch('contrib.bind.zone.Zone.to_file')
    def test_save(self, fwm):
        zp = ZoneParser('example.com')
        zp.save('/tmp')
        fwm.assert_called_with(outpath='/tmp', domain='example.com')

    @patch('contrib.bind.zoneparser.ZoneParser.id_generator')
    @patch('subprocess.call')
    @patch('os.path.exists')
    def test_normalize_contents(self, opem, spm, idm):
        idm.return_value = 'ABC123'
        opem.return_value = True
        zp = ZoneParser('example.com')
        zp.zonefile = '/tmp/foobar'
        zp.normalize_contents('/tmp/foobar')
        spm.assert_called_with(['named-checkzone', '-o', '/tmp/ABC123',
                                'example.com', '/tmp/foobar'])
