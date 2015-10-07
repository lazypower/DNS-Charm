import unittest
from mock import patch, Mock, MagicMock
import os
import sys

from bind.provider import Provider


class TestBindProvider(unittest.TestCase):


    @patch('subprocess.check_output')
    @patch('bind.provider.unit_get')
    def test_first_setup(self, ugm, spcom):
        ugm.return_value = '10.0.0.1'
        bp = Provider('example.com')
        parser = MagicMock()
        bp.first_setup(parser)
        ugm.assert_called_once_with('public-address')
        parser.dict_to_zone.assert_called_with({'rr': 'A', 'alias': 'ns',
                                                'addr': '10.0.0.1',
                                                'ttl': 300})

    @patch('bind.provider.ZoneParser.dict_to_zone')
    @patch('bind.provider.ZoneParser.save')
    def test_add_record(self, zps, zpm):
        bp = Provider('example.com')
        bp.reload_config = Mock()
        bp.add_record({'rr': 'A', 'alias': 'foo', 'addr': '127.0.0.1'})
        zps.assert_called_once_with()
        zpm.assert_called_once_with({'alias': 'foo', 'addr': '127.0.0.1', 'rr': 'A'})
        bp.reload_config.assert_called_once_with()


