from common import provider_keys
from os import path
import shlex
import subprocess

def install():
    requirements= path.join(path.dirname(__file__), 'rt53-requirements.txt')
    #import ipdb; ipdb.set_trace()
    if path.exists(requirements):
        cmd = "pip install -r rt53-requirements.txt"
        subprocess.check_call(shlex.split(cmd))
    else:
        raise IOError("Missing rt53-requirements.txt")


    # validate that we have credentials as a preliminary sanity check
    keys = provider_keys()
    if not 'AWS_ACCESS_KEY' in keys or not 'AWS_SECRET_KEY' in keys:
        raise ValueError("Missing provider API keys: AWS_ACCESS_KEY or"
                          " AWS_SECRET_KEY")


