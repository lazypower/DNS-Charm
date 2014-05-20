import urllib2

from charmhelpers.core.hookenv import log
from charmhelpers.fetch import (
    apt_update,
    apt_install,
)


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


def install_common():
    log("Preparing for API Wrapper installation")
    apt_update(fatal=True)
    apt_install(packages=[
        'git-core'
    ], fatal=True)
