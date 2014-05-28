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
    ez = []

    def setUp(self):
        with open('contrib/tests/fixtures/sample_bind_parsed') as f:
            self.ez = f.readlines()
        self.ezp = list(self.ez)

    def test_init_loads_keys_from_zone_class(self):
        zp = ZoneParser('example.com')
        self.assertIn('aaaa', zp.implemented_records)

    @patch('contrib.bind.zoneparser.tldextract.extract')
    @patch('subprocess.call')
    @patch('os.path.exists')
    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file(self, mopen, mose, spcm, tldem):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez
        mose.return_value = True
        tldem.return_value('example.com')
        zp = ZoneParser('ns')
        self.assertTrue(len(zp.contents) == 5)

    @patch('contrib.bind.zoneparser.ZoneParser.a_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.aaaa_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.cname_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.ns_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.soa_from_array')
    def test_array_to_zone(self, soam, nsm, cnm, aam, am):
        zp = ZoneParser('example.com')
        zp.contents = self.ez
        zp.array_to_zone()
        soam.assert_called_with(self.ez[0].split())
        nsm.assert_called_with(self.ez[1].split())
        # cnm.assert_called_with(self.ez[4].split('\t'))
        am.assert_called_with(self.ez[4].split())

    def test_soa_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez
        zp.soa_from_array(zcontents[0].split())
        self.assertEqual(zp.zone.contents['soa'], [{'addr': 'ns.example.com.',
                                                'owner': 'root.example.com.',
                                                'expiry': '1814400',
                                                'minimum': '900',
                                                'refresh': '43200',
                                                'serial': '2003080800',
                                                'ttl': '604800',
                                                'update-retry': '900'}])

    def test_cname_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez
        zp.cname_from_array(zcontents[3].split())
        self.assertEqual(zp.zone.contents['cname'], [{'ttl': '604800',
                                                      'alias': 'ns',
                                                      'addr': 'ns1.example.com.'}])

    def test_a_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez
        zp.a_from_array(zcontents[2].split('\t'))
        self.assertEqual(zp.zone.contents['a'], [{'ttl': '604800',
                                                  'addr': '10.0.3.103',
                                                  'alias': ''}])

    @patch('contrib.bind.zone.Zone.to_file')
    def test_save(self, fwm):
        zp = ZoneParser('example.com')
        zp.save()
        fwm.assert_called_with('/etc/bind/db.example.com')

    @patch('contrib.bind.zoneparser.ZoneParser.id_generator')
    @patch('subprocess.call')
    @patch('os.path.exists')
    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_normalize_contents(self, mopen, opem, spm, idm):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez
        idm.return_value = 'ABC123'
        opem.return_value = True
        zp = ZoneParser('example.com')
        zp.normalize_contents()
        spm.assert_called_with(['named-checkzone', '-o', '/tmp/ABC123',
                                'example.com', '/etc/bind/db.example.com'])
