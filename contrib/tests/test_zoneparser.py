import sys
import unittest
from mock import (
    patch,
    Mock,
)

from contrib.bind.zoneparser import ZoneParser
# from contrib.bind.zone import Zone


class TestZoneParser(unittest.TestCase):

    ez = []

    def setUp(self):
        with open('contrib/tests/fixtures/sample_bind_parsed') as f:
            self.ez = f.readlines()
        self.ezp = list(self.ez)

    def test_init_loads_keys_from_zone_class(self):
        zp = ZoneParser('example.com')
        self.assertIn('CNAME', zp.implemented_records)
        self.assertIn('AAAA', zp.implemented_records)
        self.assertIn('A', zp.implemented_records)
        self.assertIn('SOA', zp.implemented_records)
        self.assertIn('NS', zp.implemented_records)

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file(self, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = self.ez
        zp = ZoneParser('ns')
        zp.normalize_contents = Mock()
        zp.normalize_contents.return_value = self.ez
        self.assertEqual(zp.from_file(), self.ez)

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file_exception(self, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines = Mock(side_effect=OSError('Intentional'))
        zp = ZoneParser('foo.com')
        zp.normalize_contents = Mock()
        zp.normalize_contents.return_value = self.ez
        self.assertEqual(zp.from_file(), [])

    def test_id_generator(self):
        zp = ZoneParser('foo.com')
        self.assertTrue(len(zp.id_generator(6)) == 6)

    def test_sanity(self):
        zp = ZoneParser('foo.com')

    @patch('contrib.bind.zoneparser.ZoneParser.a_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.cname_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.ns_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.soa_from_array')
    def test_array_to_zone(self, soam, nsm, cnm, am):
        zp = ZoneParser('example.com')
        zp.contents = self.ez
        zp.array_to_zone()
        soam.assert_called_with(self.ez[0].split())
        nsm.assert_called_with(self.ez[1].split())
        cnm.assert_called_with(self.ez[3].split())
        am.assert_called_with(self.ez[4].split())

    def test_soa_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez
        zp.soa_from_array(zcontents[0].split())
        self.assertEqual(zp.zone.contents['SOA'], [{'addr': 'ns.example.com.',
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
        self.assertEqual(zp.zone.contents['CNAME'], [{'ttl': '604800',
                                                      'alias': 'ns',
                                                      'addr': 'ns1.example.com.'}])

    def test_a_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = self.ez
        zp.a_from_array(zcontents[2].split('\t'))
        self.assertEqual(zp.zone.contents['A'], [{'ttl': '604800',
                                                  'addr': '10.0.3.103',
                                                  'alias': '@'}])

    def test_naptr_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = '@ 3200 IN NAPTR 1 1 "S" "SIP+D2T" "" _sip._tcp'.split(' ')
        zp.naptr_from_array(zcontents)
        self.assertEqual(zp.zone.contents['NAPTR'], [{'alias': '@',
                                                      'order': '1',
                                                      'pref': '1',
                                                      'flag': '"S"',
                                                      'params': '"SIP+D2T"',
                                                      'regexp': '""',
                                                      'replace': '_sip._tcp'}])

    def test_srv_from_array(self):
        zp = ZoneParser('example.com')
        zcontents = '_sip._udp 3200 IN SRV 0 0 5060 bono-0'.split(' ')
        zp.srv_from_array(zcontents)
        self.assertEqual(zp.zone.contents['SRV'], [{'alias': '_sip._udp',
                                                    'priority': '0',
                                                    'weight': '0',
                                                    'port': '5060',
                                                    'target': 'bono-0'}])

    def test_bono_a_from_array(self):
        zp = ZoneParser('offline.cw-ngv.com')
        zp.a_from_array(u'@ 300 IN A 54.73.45.41'.split(' '))
        self.assertEqual(zp.zone.contents['A'], [{'ttl': '300',
                                                  'addr': '54.73.45.41',
                                                  'alias': '@'}])

    def test_ellis_a_from_array(self):
        zp = ZoneParser('offline.cw-ngv.com')
        zp.a_from_array(u'ellis-0 300 IN A 54.73.45.41'.split(' '))
        self.assertEqual(zp.zone.contents['A'], [{'ttl': '300',
                                                  'addr': '54.73.45.41',
                                                  'alias': 'ellis-0'}])       

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    @patch('contrib.bind.zone.Zone.to_file')
    def test_save(self, fwm, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = """
zone "localhost" {
        type master;
        file "/etc/bind/db.local";
};

zone "127.in-addr.arpa" {
        type master;
        file "/etc/bind/db.127";
};""".split('\n')


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

    def test_find_type(self):
        zp = ZoneParser('example.com')
        self.assertEqual(zp.find_type(['foo', 'bar', 'baz', 'CNAME']), 3)
        self.assertEqual(zp.find_type(['foo', 'bar', 'baz']), -1)

    def test_dict_to_zone(self):
        zp = ZoneParser('example.com')
        zp.update_ns = Mock()
        zp.update_soa = Mock()
        zp.update_cname = Mock()
        zp.update_a = Mock()
        zp.dict_to_zone({'rr': 'NS'})
        zp.update_ns.assert_called_with({'rr': 'NS'})
        zp.dict_to_zone({'rr': 'SOA'})
        zp.update_soa.assert_called_with({'rr': 'SOA'})
        zp.dict_to_zone({'rr': 'CNAME'})
        zp.update_cname.assert_called_with({'rr': 'CNAME'})
        zp.dict_to_zone({'rr': 'A'})
        zp.update_a.assert_called_with({'rr': 'A'})
        zp.dict_to_zone({'rr': 'NOPE'})

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_read_default_zones(self, mopen):
        seed_zone = """zone "255.in-addr.arpa" {
    type master;
    file "/etc/bind/db.255";
};"""
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = seed_zone.split('\n')
        zp = ZoneParser('example.com')
        self.assertEqual(zp.read_default_zones(), seed_zone.split('\n'))

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_write_default_zones(self, mopen):
        seed_zone = """zone "255.in-addr.arpa" {
    type master;
    file "/etc/bind/db.255";
};"""
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.write = Mock()
        made_config = seed_zone.split('\n').append(['hello'])
        zp = ZoneParser('example.com')
        zp.write_default_zones(made_config)
        # mopen.return_value.write.assert_called_with(made_config)

    def test_exists_in_default_zones(self):
        seed_zone = """zone "example.com" {
    type master;
    file "/etc/bind/db.example.com";
};""" 
        zp = ZoneParser('example.com')
        self.assertEqual(zp.exists_in_default_zones(seed_zone.split('\n')), 0)
        zp = ZoneParser('nope.com')
        self.assertEqual(zp.exists_in_default_zones(seed_zone.split('\n')), -1)
