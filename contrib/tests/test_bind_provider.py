import unittest
from mock import patch, Mock, MagicMock
import os
import sys

from contrib.bind.provider import BindProvider

sys.path.insert(0, os.path.abspath(os.path.join('..', '..',
                                                'lib', 'charmhelpers')))


class TestBindProvider(unittest.TestCase):

    @patch('contrib.bind.provider.open_port')
    @patch('contrib.bind.provider.apt_update')
    @patch('contrib.bind.provider.apt_install')
    @patch('contrib.bind.provider.config')
    @patch('contrib.bind.provider.log')
    @patch('contrib.bind.provider.install_packages')
    @patch('contrib.bind.provider.pip_install')
    def test_install(self, pim, ipm, logm, cfgm, aim, aum, opm):
        bp = BindProvider()
        bp.reload_config = Mock()
        cfgm.return_value={'offline': False, 'domain': 'example.com'}
        bp.install()
        aum.assert_called_with(fatal=True)
        aim.assert_called_with(packages=['bind9', 'dnsutils'], fatal=True)
        bp.reload_config.assert_called_once()
        cfgm.return_value={'offline': True, 'domain': 'example.com'}
        bp.install()
        pim.assert_called_once()
        ipm.assert_called_once()
        bp.reload_config.assert_called_once()

    @patch('contrib.bind.provider.unit_get')
    def test_first_setup(self, ugm):
        bp = BindProvider()
        parser = MagicMock()
        bp.first_setup(parser)
        ugm.assert_called_once()
        parser.dict_to_zone.assert_called_with({'rr': 'CNAME', 'alias': 'ns',
                                                'addr': 'ns1.example.com.',
                                                'ttl': 300})

    @patch('contrib.bind.provider.ZoneParser.dict_to_zone')
    @patch('contrib.bind.provider.ZoneParser.save')
    def test_add_record(self, zps, zpm):
        bp = BindProvider()
        bp.reload_config = Mock()
        bp.add_record({'rr': 'A', 'alias': 'foo', 'addr': '127.0.0.1'})
        zps.assert_called_once()
        zpm.assert_called_once()
        bp.reload_config.assert_called_once()

    @patch('contrib.bind.provider.ZoneParser.save')
    @patch('os.path.exists')
    def test_config_changed(self, osem, zpsm):
        osem.return_value = False
        bp = BindProvider()
        bp.reload_config = Mock()
        bp.first_setup = Mock()
        bp.config_changed()
        bp.first_setup.assert_called_once()
        zpsm.assert_called_once()
        bp.reload_config.assert_called_once()

    @patch('contrib.bind.provider.ZoneParser')
    def test_remove_record(self, zpm):
        bp = BindProvider()
        bp.reload_config = Mock()
        zpm.zone.remove = Mock()
        zpm.save = Mock()
        bp.remove_record({'rr': 'A', 'alias': 'ns'})
        zpm.save.assert_called_once()
        bp.reload_config.assert_called_once()
