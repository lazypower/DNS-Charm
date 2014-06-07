import unittest
from mock import patch, Mock, MagicMock
import os
import sys

from contrib.bind.provider import BindProvider

sys.path.insert(0, os.path.abspath(os.path.join('..', '..',
                                                'lib', 'charmhelpers')))


class TestBindProvider(unittest.TestCase):


    @patch('subprocess.check_output')
    @patch('contrib.bind.provider.unit_get')
    def test_first_setup(self, ugm, spcom):
        spcom.return_value = '10.0.0.1'
        bp = BindProvider()
        parser = MagicMock()
        bp.first_setup(parser)
        ugm.assert_called_once()
        parser.dict_to_zone.assert_called_with({'rr': 'A', 'alias': 'ns',
                                                'addr': '10.0.0.1',
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
