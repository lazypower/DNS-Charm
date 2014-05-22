import sys
import os
import urllib2

print sys.path

import unittest
from mock import (
    patch,
    Mock,
)

sys.path.insert(0, os.path.abspath(os.path.join('..', 'lib', 'charmhelpers')))

from hooks import common


class TestCommon(unittest.TestCase):

    @patch('hooks.common.config')
    @patch('hooks.common.log')
    def test_sanity_check_configured(self, lmock, cfgmock):
        cfgmock.return_value = {'assume_provider': True,
                                'canonical_domain': 'example.com'}
        self.assertTrue(common.sanity_check())
        cfgmock.assert_called_once(common.sanity_check())

    @patch('hooks.common.config')
    @patch('hooks.common.log')
    def test_sanity_check_unconfigured(self, lmock, cfgmock):
        cfgmock.return_value = {'assume_provider': True,
                                'canonical_domain': ''}
        self.assertFalse(common.sanity_check())
        cfgmock.assert_called_once(common.sanity_check())

    @patch('hooks.common.mkdir')
    def test_make_bind_store(self, mkdrmock):
        common.make_bind_store()
        mkdrmock.assert_called_with('/etc/bind/zones')

    @patch('builtins.open' if sys.version_info > (3,) else '__builtin__.open')
    def test_existing_nameservers(self, omck):
        omck.return_value.__enter__ = lambda s: s
        omck.return_value.__exit__ = Mock()
        omck.return_value.readlines.return_value = [
            'nameserver 127.0.0.1',
            'search maas',
            'nameserver 10.0.1.1',
            'search foobar']
        nameservers = common.existing_nameservers()
        self.assertEqual(nameservers, ['127.0.0.1', '10.0.1.1'])

    @patch('hooks.common.urllib2.urlopen')
    def test_am_i_online(self, urlmock):
        common.am_i_online()
        urlmock.assert_called_with('http://74.125.228.100', timeout=1)

    @patch('hooks.common.urllib2.urlopen')
    def test_am_i_online_raises_error(self, urlmock):
        urlmock.side_effect = [urllib2.URLError('nope')]
        self.assertFalse(common.am_i_online())
