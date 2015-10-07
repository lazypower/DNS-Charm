import sys
import os

import unittest
from mock import (
    patch,
    Mock,
)

import common


class TestCommon(unittest.TestCase):

    @patch('common.config')
    @patch('common.log')
    def test_sanity_check_configured(self, lmock, cfgmock):
        cfgmock.return_value = {'assume_provider': True,
                                'domain': 'example.com'}
        self.assertTrue(common.sanity_check())

    @patch('common.config')
    @patch('common.log')
    def test_sanity_check_unconfigured(self, lmock, cfgmock):
        cfgmock.return_value = {'assume_provider': True,
                                'domain': ''}
        self.assertFalse(common.sanity_check())

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

    @patch('os.listdir')
    @patch('subprocess.call')
    def test_install_packages(self, spcm, osldm):
        osldm.return_value = ['foo.deb', 'bar.deb']
        common.install_packages('/tmp/nope')
        spcm.assert_called_with(['dpkg', '-i', '/tmp/nope/bar.deb'])

    @patch('os.listdir')
    @patch('subprocess.call')
    def test_pip_install(self, spcm, osldm):
        osldm.return_value = ['foo.tar.gz']
        common.pip_install('/tmp/nope')
        spcm.assert_called_with(['pip', 'install', '/tmp/nope/foo.tar.gz'])

    def test_return_sub(self):
        sub = common.return_sub('example.com', 'foo.example.com')
        self.assertEqual('foo', sub)

    def test_return_sub_with_sub_domain(self):
        sub = common.return_sub('offline.example.com',
                                'foo.offline.example.com')
        self.assertEqual('foo', sub)

    def test_return_sub_will_return_empty(self):
        sub = common.return_sub('example.com',
                                'example.com')
        self.assertEqual('', sub)

    def test_return_sub_return_with_named_checkzone_output(self):
        sub = common.return_sub('example.com', 'example.com.')
        self.assertEqual('', sub)

# This test is highly dependent on the environment itself and fails in
# CI consistently as the host has improper DNS resolution. /etc/hosts
# has localhost defined, but is not working properly. so rely on the mock
# to really determine if the method works as expected.
#    def test_hostname_resolution(self):
#        ip = common.resolve_hostname_to_ip('localhost')
#        self.assertEqual('127.0.0.1', ip)

    @patch('subprocess.check_output')
    def test_maas_funky_dig_resolution(self, spm):
        spm.return_value = "'10-0-10-55.maas.\n10.0.10.55"
        ip = common.resolve_hostname_to_ip('localhost')
        self.assertEqual('10.0.10.55', ip)

    def test_trim(self):
        a = ['a', '', '', 'b']
        trimmed = common.trim_empty_array_elements(a)
        self.assertEqual(['a','b'], trimmed)

    @patch('common.config')
    def test_provider_keys(self, cfgmock):
        cfgmock.return_value = 'awsKey|12345 awsSecret|abc123def'
        keys = common.provider_keys()
        self.assertEqual(keys['awsKey'], '12345')
        self.assertEqual(keys['awsSecret'], 'abc123def')

