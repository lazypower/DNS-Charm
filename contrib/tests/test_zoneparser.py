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
        with open('contrib/tests/fixtures/db.orangebox.com') as f:
            self.ez = f.readlines()
        self.ezp = list(self.ez)

    def test_init_loads_keys_from_zone_class(self):
        zp = ZoneParser('example.com')
        self.assertIn('CNAME', zp.implemented_records)
        self.assertIn('AAAA', zp.implemented_records)
        self.assertIn('A', zp.implemented_records)
        self.assertIn('SOA', zp.implemented_records)
        self.assertIn('NS', zp.implemented_records)
        self.assertIn('NAPTR', zp.implemented_records)
        self.assertIn('SRV', zp.implemented_records)

    # @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    # def test_from_file(self, mopen):
    #     mopen.return_value.__enter__ = lambda s: s
    #     mopen.return_value.__exit__ = Mock()
    #     mopen.return_value.readlines.return_value = self.ez
    #     zp = ZoneParser('orangebox.com')
    #     mopen.assert_called_with('/etc/bind/db.orangebox.com')

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_from_file_exception(self, mopen):
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines = Mock(side_effect=OSError('Intentional'))
        zp = ZoneParser('foo.com')
        zp.normalize_contents = Mock()
        zp.normalize_contents.return_value = self.ez
        self.assertEqual(zp.from_file(), [])

    @patch('contrib.bind.zoneparser.ZoneParser.a_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.ns_from_array')
    @patch('contrib.bind.zoneparser.ZoneParser.soa_from_array')
    def test_array_to_zone(self, soam, nsm, am):
        zp = ZoneParser('orangebox.com')
        zp.contents = self.ez
        zp.array_to_zone()
        soam.assert_called_with(self.ez[5].split())
        nsm.assert_called_with(self.ez[6].split())
        am.assert_called_with(self.ez[7].split())

    def test_soa_from_array(self):
        zp = ZoneParser('orangebox.com')
        zp.soa_from_array(self.ez[5].split())
        self.assertEqual(zp.zone.contents['SOA'],
                         [{'addr': 'ns.orangebox.com.',
                           'owner': 'root.orangebox.com.',
                           'expiry': '3w',
                           'minimum': '15m',
                           'refresh': '12h',
                           'serial': '16640992',
                           'update-retry': '15m'}])

    def test_cname_from_array(self):
        zp = ZoneParser('orangebox.com')
        zp.cname_from_array(self.ez[8].split())
        self.assertEqual(zp.zone.contents['CNAME'], [{'alias': 'mail',
                                                      'addr': 'gmail.com.'}])

    def test_a_from_array(self):
        zp = ZoneParser('orangebox.com')
        zp.a_from_array(self.ez[7].split())
        self.assertEqual(zp.zone.contents['A'], [{'addr': '10.0.10.55',
                                                  'alias': 'ns'}])

    def test_a_from_array_with_ttl(self):
        zp = ZoneParser('orangebox.com')
        zp.a_from_array(['ns', '300', 'A', '10.0.10.55'])
        self.assertEqual(zp.zone.contents['A'], [{'addr': '10.0.10.55',
                                                  'alias': 'ns',
                                                  'ttl': '300'}])

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
    def test_read_local_zones(self, mopen):
        seed_zone = """zone "255.in-addr.arpa" {
    type master;
    file "/etc/bind/db.255";
};"""
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.readlines.return_value = seed_zone.split('\n')
        zp = ZoneParser('example.com')
        self.assertEqual(zp.read_local_zones(), seed_zone.split('\n'))

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_write_local_zones(self, mopen):
        seed_zone = """zone "255.in-addr.arpa" {
    type master;
    file "/etc/bind/db.255";
};"""
        mopen.return_value.__enter__ = lambda s: s
        mopen.return_value.__exit__ = Mock()
        mopen.return_value.write = Mock()
        made_config = seed_zone.split('\n').append(['hello'])
        zp = ZoneParser('example.com')
        zp.write_local_zones(made_config)
        # mopen.return_value.write.assert_called_with(made_config)

    def test_exists_in_local_zones(self):
        seed_zone = """zone "example.com" {
    type master;
    file "/etc/bind/db.example.com";
};"""
        zp = ZoneParser('example.com')
        self.assertEqual(zp.exists_in_local_zones(seed_zone.split('\n')), 0)
        zp = ZoneParser('nope.com')
        self.assertEqual(zp.exists_in_local_zones(seed_zone.split('\n')), -1)
