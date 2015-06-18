from mock import patch, Mock
import pytest


from rt53 import install

class TestRt53Installer():

    def test_install_missing_requirements(self):
        with patch('rt53.install.path.exists') as pmock:
            pmock.return_value = False
            with pytest.raises(IOError):
                install.install()

    @patch('common.config')
    def test_install_pip_command(self, cfgmock):
        cfgmock.return_value = 'AWS_ACCESS_KEY_ID|123 AWS_SECRET_ACCESS_KEY|abc'
        with patch('rt53.install.subprocess') as spmock:
            spmock.check_call.return_value.returncode = 0
            install.install()
            assert(
                spmock.called_with(['pip', 'install', '-r', 'rt53-requirements.txt'])
            )

