import os
import sys

# Add charmhelpers to the system path.
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.environ['CHARM_DIR'],
                                                    'lib')))
except:
    sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'lib')))

from charmhelpers.core.hookenv import open_port, config, log

from charmhelpers.fetch import (
    apt_install,
    apt_update,
)
from common import install_packages, pip_install


class ProviderInstaller(object):
    def __init__(self):
        self.install()

    def install(self):
        if config()['offline'] is False:
            apt_update(fatal=True)
            apt_install(packages=[
                'bind9',
                'dnsutils',
                ], fatal=True)
        else:
            log("Installing offline debian packages")
            install_packages('files/bind')
            # rerun cuz its buggy
            install_packages('files/bind')
            log("Installing Python packages")
            pip_install('files/bind/pip')

        os.makedirs('/etc/bind/zone-backup')
        open_port(53)
