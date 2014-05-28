import os
import sys
import urllib2
import tldextract

# Add charmhelpers to the system path.
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.environ['CHARM_DIR'],
                                                    'lib')))
except:
    sys.path.insert(0, os.path.abspath(os.path.join('..', 'lib')))


from charmhelpers.core.hookenv import (
    log,
    config,
    unit_get,
)

from charmhelpers.fetch import (
    apt_install,
    apt_update,
)


def sanity_check():
    if not config()['canonical_domain']:
        log("No Canonical Domain specified - Aborting until configured")
        # It's reasonable to assume we're not doing anything useful at this
        # point, as we are unconfigured. Abort doing *anything*
        return False
    return True


# ###########
# Environment Probing / Modifications
# ###########


# Parse existing nameservers from resolv.conf
def existing_nameservers():
    dns_servers = []
    with open('/etc/resolv.conf') as f:
        contents = f.readlines()
        for line in contents:
            if line.find('nameserver') != -1:
                dns_servers.append(line.replace('nameserver ', '').rstrip())
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
