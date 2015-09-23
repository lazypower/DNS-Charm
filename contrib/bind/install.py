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
    ## use the nameserver in /etc/resolv.conf as a forwarder ...
    import DNS
    DNS.ParseResolvConf("/etc/resolv.conf")
    nameserver = DNS.defaults['server'][0]
    log('Setting dns to be forwarder to :'+nameserver)
    import jinja2
    templateLoader = jinja2.FileSystemLoader( searchpath= os.environ['CHARM_DIR'] )
    #use Jinja2 template to enable bind forwarding
    templateEnv=jinja2.Environment( loader=templateLoader );
    template=templateEnv.get_template('contrib/bind/templates/named.conf.options.jinja2')
    output_from_parsed_template = template.render(forwarder=nameserver)
    # to save the results
    with open("/etc/bind/named.conf.options", "wb") as fh:
        fh.write(output_from_parsed_template)
        ## use jinja2 templates..


    if not os.path.exists('/etc/bind/zone-backup'):
        os.makedirs('/etc/bind/zone-backup')
    open_port(53, "TCP")
    open_port(53, "UDP")
