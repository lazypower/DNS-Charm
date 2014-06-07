import os
import subprocess
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


def trim_empty_array_elements(data):
    val = [line for line in data if line.strip()]
    print("TRIM: %s" % val)
    return val


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


def return_sub(domain, address):
    address = address.rstrip('.')
    return address[:-len(domain)].rstrip('.')


def resolve_hostname_to_ip(hostname):
    hostname = hostname.strip()
    out = subprocess.check_output(['dig', '+short', hostname]).rstrip('\n')
    # required to obtain the IP from MAAS output. See test_common - line 83
    return out.split('\n')[-1]


# Parse existing nameservers from resolv.conf
def existing_nameservers():
    dns_servers = []
    with open('/etc/resolv.conf') as f:
        contents = f.readlines()
        for line in contents:
            if line.find('nameserver') != -1:
                dns_servers.append(line.replace('nameserver ', '').rstrip())
    return dns_servers
