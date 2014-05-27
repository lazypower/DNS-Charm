import unittest
from mock import patch, Mock
import os
import sys

from contrib.bind.provider import BindProvider

sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'lib', 'charmhelpers')))

class TestBindProvider(unittest.TestCase):

    @patch('contrib.bind.provider.apt_update')
    @patch('contrib.bind.provider.apt_install')
    def test_install(self, aim, aum):
        bp = BindProvider()
        bp.install()
        aum.assert_called_with(fatal=True)
        aim.assert_called_with(packages=['bind9', 'dnsutils'], fatal=True)
