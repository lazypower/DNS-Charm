import importlib
import json
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
    if domain in address:
        return address[:-len(domain)].rstrip('.')
    else:
        return address


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

def load_module(full_class_string):
    """
    dynamically load a module from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])

    return importlib.import_module(module_path)

def load_class(full_class_string):
    """
    dynamically load a class from a string
    """

    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    return getattr(module, class_str)

def provider_keys():
    """
    load the space separated key/value pairs and return a dictionary
    args of conf for easy stub in unit-tests
    """
    if not config('provider_keys'):
        raise ValueError("Missing required config value for provider_keys")

    provider_config = {}
    # load the keys into an array for iteration
    pkeys = config('provider_keys').split(' ')
    for k in pkeys:
        if not k: continue
        provider_config[k.split('|')[0]] = k.split('|')[1]
    return provider_config

def serialize_data(datafile, data):
    from path import Path
    p = Path(datafile)
    p.dirname().mkdir_p()

    with open(p, 'w+') as f:
        f.write(json.dumps(data))

def unserialize_data(datafile):
    from path import Path
    p = Path(datafile)
    if p.exists():
        with open(p, 'r') as f:
            return json.loads(f.read())
    else:
        return {}
