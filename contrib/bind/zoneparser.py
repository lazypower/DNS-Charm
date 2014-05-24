import logging
import os
import random
import subprocess
import string
from .zone import Zone

import ipdb

# Note about how this is constructed. BIND ships with a tool called
# named-checkzone. This normalizes ALL output from a bind file, and
# allows this class to make some assumptions about placement of values.
# Anything loaded from file here will be passed through this utility.
# If it fails to normalize/parse the file, then the operation will fail.

# I'm open to suggestions on how to do this outside of relying on binds
# wrapping normalizer, as Ideally this should be a bit more robust than
# that.

logging.basicConfig(level=logging.INFO)

class ZoneParser(object):

    def __init__(self, domain, file_handle=None):
        self.zone = Zone()
        self.domain = domain
        self.implemented_records = self.zone.contents.keys()
        if file_handle:
            self.contents = self.from_file(file_handle)

    def from_file(self, file_handle):
        contents = []
        normalized_file = self.__normalize_contents(file_handle)
        with open(normalized_file) as f:
            for line in f.readlines():
                contents.append(line)
        return contents

    def __normalize_contents(self, file_handle):
        if os.path.exists(file_handle):
            rando = self.__id_generator(8)
            rando_filepath = "/tmp/%s" % rando
            logging.info('created temporary file %s' % rando_filepath)
            subprocess.call(['named-checkzone', '-o', rando_filepath,
                             self.domain, file_handle])
            return rando_filepath

    # TODO: Make this do something
    def from_dict(self, dns_records):
        self.__validate_attributes(dns_records)


    def __validate_attributes(self, configuration):
            if configuration['type'] not in self.implemented_records:
                raise KeyError("Unknown key %s" % configuration['type'])

    def __id_generator(self, size=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))
