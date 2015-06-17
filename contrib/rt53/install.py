from common import provider_keys
from os import path, getenv
import shlex
import subprocess

def install():
    requirements= path.join(path.dirname(__file__), 'rt53-requirements.txt')
    if path.exists(requirements):
        cmd = "pip install -r {}/contrib/rt53/rt53-requirements.txt".format(
                getenv('CHARM_DIR'))
        subprocess.check_call(shlex.split(cmd))
    else:
        raise IOError("Missing rt53-requirements.txt")

    # validate that we have credentials as a preliminary sanity check
    try:
        provider_keys()
    except ValueError:
        print "Missing provider API keys: AWS_ACCESS_KEY_ID or" \
                          " AWS_SECRET_ACCESS_KEY"
        print "config-changed will fail... incoming failure in 3..2..."
