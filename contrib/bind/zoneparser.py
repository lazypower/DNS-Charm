import logging
import os
import random
import subprocess
import string
import tldextract
from .zone import Zone

import ipdb

# Note about how this is constructed. BIND ships with a tool called
# named-checkzone. This normalizes ALL output from a bind file, and
# allows this class to make some assumptions about placement of values.
# Anything loaded from file here will be passed through this utility.
# If it fails to normalize/parse the file, then the operation will fail.

# I'm open to suggestions on how to do this outside of relying on bind's
# wrapping normalizer

logging.basicConfig(level=logging.INFO)


class ZoneParser(object):

    def __init__(self, domain, file_handle=None):
        self.zone = Zone()
        self.domain = domain
        self.implemented_records = self.zone.contents.keys()
        self.tldxtr = tldextract.extract
        if file_handle:
            self.zonefile = file_handle
            self.contents = self.from_file(file_handle)
            self.array_to_zone()

    def from_file(self, file_handle):
        contents = []
        normalized_file = self.__normalize_contents(file_handle)
        with open(normalized_file) as f:
            for line in f.readlines():
                contents.append(line)
        return contents

    # ####################################
    # Utility Methods
    # ####################################

    # Create an intermediate file to warehouse the normalized config
    def __normalize_contents(self, file_handle):
        if os.path.exists(file_handle):
            rando = self.__id_generator(8)
            rando_filepath = "/tmp/%s" % rando
            subprocess.call(['named-checkzone', '-o', rando_filepath,
                             self.domain, file_handle])
            logging.info('created temporary file %s' % rando_filepath)
            return rando_filepath

    def __validate_attributes(self, configuration):
            if configuration['type'] not in self.implemented_records:
                raise KeyError("Unknown key %s" % configuration['type'])

    def __id_generator(self, size=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    # #######################################
    # Parsing Array to Zone Dictionary - this is going
    # to be a bit messy, and specific to loading
    # from the named-checkzone utility - this is brittle
    # #######################################

    def failed_check(self):
            raise IndexError("Array Notation should conform to named-checkzone"
                             " specification")

    def a_from_array(self, data):
        if len(data) < 6:
            self.failed_check()
        ttl = data[4].strip().split(' IN')[0]
        addr = data[6].strip()
        alias = self.tldxtr(data[0].strip()).subdomain
        parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        self.zone.a(parsed)

    def aaaa_from_array(self, data):
        if len(data) < 6:
            self.failed_check()
        ttl = data[4].strip().split(' IN')[0]
        addr = data[6].strip()
        alias = self.tldxtr(data[0].strip()).subdomain
        parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        self.zone.aaaa(parsed)

    def cname_from_array(self, data):
        if len(data) < 6:
            self.failed_check()
        ipdb.set_trace()

    def ns_from_array(self, data):
        if len(data) < 6:
            self.failed_check()
        ttl = data[4].strip().split(' IN')[0]
        owner_name = "%s." % self.domain
        alias = data[6].strip()
        parsed = {'ttl': ttl, 'alias': alias, 'owner-name': owner_name}
        self.zone.ns(parsed)

    def soa_from_array(self, data):
        if len(data) < 6:
            self.failed_check()
        logging.info(data)
        agg = data[6].strip().split(' ')
        ttl = data[4].strip().split(' IN')[0]
        addr = agg[0]
        alias = agg[1]
        serial = agg[2]
        refresh = agg[3]
        update_retry = agg[4]
        expiry = agg[5]
        minimum = agg[6]
        parsed = {'ttl': ttl, 'addr': addr, 'alias': alias, 'serial': serial,
                  'refresh': refresh, 'update-retry': update_retry,
                  'expiry': expiry, 'minimum': minimum}
        self.zone.soa(parsed)

    def array_to_zone(self):
        if not self.contents:
            raise ValueError("Missing Zone Contents")

        for entry in self.contents:
            line = entry.split('\t')
            logging.info(line)
            dclass = line[5]
            for case in switch(dclass):
                if case('A'):
                    self.a_from_array(line)
                    break
                if case('AAAA'):
                    self.aaaa_from_array(line)
                    break
                if case('CNAME'):
                    self.cname_from_array(line)
                    break
                if case('NS'):
                    self.ns_from_array(line)
                    break
                if case('SOA'):
                    self.soa_from_array(line)
                    break
                if case():
                    logging.warning('Unable to match type %s' % dclass)


# Python doesn't give us a switch case statement, so replicate it here.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:
            self.fall = True
            return True
        else:
            return False
