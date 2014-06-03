import os
import sys
import subprocess

# Add charmhelpers to the system path.
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.environ['CHARM_DIR'],
                                                    'lib')))
except:
    sys.path.insert(0, os.path.abspath(os.path.join('..', 'lib')))


from charmhelpers.core.hookenv import (
    log,
    config,
)


def sanity_check():
    if not config()['domain']:
        log("No Base Domain specified - Aborting until configured")
        # It's reasonable to assume we're not doing anything useful at this
        # point, as we are unconfigured. Abort doing *anything*
        return False
    return True


def install_packages(path):
    packages = os.listdir(path)
    for pkg in packages:
        pkg = "%s/%s" % (path, pkg)
        subprocess.call(['dpkg', '-i', pkg])


def pip_install(path):
    packages = os.listdir(path)
    for pkg in packages:
        pkg = "%s/%s" % (path, pkg)
        subprocess.call(['pip', 'install', pkg])


# Parse existing nameservers from resolv.conf
def existing_nameservers():
    dns_servers = []
    with open('/etc/resolv.conf') as f:
        contents = f.readlines()
        for line in contents:
            if line.find('nameserver') != -1:
                dns_servers.append(line.replace('nameserver ', '').rstrip())
    return dns_servers
