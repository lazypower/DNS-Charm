import os
import sys
import urllib2

# Add charmhelpers to the system path.
sys.path.insert(0, os.path.abspath(os.path.join('..', 'lib')))


from charmhelpers.core.hookenv import (
    log,
    config,
)
from charmhelpers.core.host import (
    mkdir,
)
from charmhelpers.fetch import (
    apt_install,
    apt_update,
)


# Convenience Methods - wrap charmhelpers
def lg(msg, level='INFO'):
    log(msg, level)


def sanity_check():
    if not config()['canonical_domain']:
        log("No Canonical Domain specified - Aborting until configured")
        # It's reasonable to assume we're not doing anything useful at this
        # point, as we are unconfigured. Abort doing *anything*
        exit(0)


# ###########
# Environment Probe / Modifications
# ###########

# Create Configuration Directories for local Bind9 Server
def make_bind_store():
    mkdir('/etc/bind')
    mkdir('/etc/bind/zones')


# Parse existing nameservers from resolv.conf
def existing_nameservers():
    contents = []
    dns_servers = []
    with open('/etc/resolv.conf') as f:
        contents = f.readlines()
    for line in contents:
        if line.find('nameserver:') != -1:
            dns_servers.append(line.replace('nameserver: ', ''))

    return dns_servers


# this is kind of arbitrary, attempt to connect to a google ip address.
# This won't be the best solution, but i'm open to ideas on how to improve
# 'onlineability' checking.
def am_i_online():
    try:
        urllib2.urlopen('http://74.125.228.100', timeout=1)
        return True
    except urllib2.URLError:
        pass
    return False


# ###########
# BIND tasks
# ###########

def install():
    sanity_check()

    log("Preparing for BIND installation")
    apt_update(fatal=True)
    apt_install(packages=[
        'bind9',
        'dnsutils',
        'python-dnspython'
    ], fatal=True)


def install_bind():
    sanity_check()

    log("Preparing for BIND installation")
    apt_update(fatal=True)
    apt_install(packages=[
        'bind9',
        'dnsutils',
        'python-dnspython'
        ], fatal=True)
