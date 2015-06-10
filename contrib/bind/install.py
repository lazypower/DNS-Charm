import os
import sys

from charmhelpers.core.hookenv import open_port, config, log

from charmhelpers.fetch import (
    apt_install,
    apt_update,
)
from common import install_packages, pip_install


def install():
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

    if not os.path.exists('/etc/bind/zone-backup'):
        os.makedirs('/etc/bind/zone-backup')
    open_port(53, "TCP")
    open_port(53, "UDP")
