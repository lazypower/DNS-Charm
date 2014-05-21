import sys
import os
import unittest
from mock import (
    patch,
)

#sys.path.insert(0, os.path.abspath(os.path.join('..', 'hooks')))
print sys.path

from hooks import common

class TestCommon(unittest.TestCase):

    @patch('charmhelpers.core.hookenv.config')
    def test_sanity_check(self, cfgmock):
        cfgmock.return_value = {'a': 'b'}
        cfgmock.assert_called_once(common.install_bind)
