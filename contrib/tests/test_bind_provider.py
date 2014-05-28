import unittest
from mock import patch, Mock
import os
import sys

from contrib.bind.provider import BindProvider

sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'lib', 'charmhelpers')))

class TestBindProvider(unittest.TestCase):

    @patch('contrib.bind.provider.apt_update')
    @patch('contrib.bind.provider.apt_install')
    @patch('contrib.bind.provider.open_port')
    def test_install(self, aim, aum, opm):
        bp = BindProvider()
        bp.install()
        aum.assert_called_with(fatal=True)
        aim.assert_called_with(packages=['bind9', 'dnsutils'], fatal=True)


    @patch('contrib.bind.parser')
    def test_first_setup(self, parm):
        bp = BindProvider()
        bp.first_setup()