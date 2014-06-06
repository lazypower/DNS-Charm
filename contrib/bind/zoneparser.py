import logging
import os
import random
import subprocess
import string
import sys
from .zone import Zone

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.environ['CHARM_DIR'],
                                                    'lib')))
except:
    sys.path.insert(0, os.path.abspath(os.path.join('..', 'lib')))

from common import trim_empty_array_elements as trim


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
        self.zonefile = "/etc/bind/db.%s" % self.domain
        self.implemented_records = self.zone.contents.keys()
        self.tldxtr = tldextract.extract
        if self.has_zone():
            self.load_and_parse('/etc/bind/db.%s' % self.domain)

    def load_and_parse(self, filepath):
        self.contents = self.from_file()
        self.array_to_zone()

    def from_file(self):
        contents = []
        normalized_file = self.normalize_contents()
        try:
            with open(normalized_file) as f:
                for line in f.readlines():
                    contents.append(line)
        except:
            logging.info('Unable to open file %s as normalized: %s' %
                        (self.zonefile, normalized_file))
        return contents

    def save(self):
        self.zone.to_file(self.zonefile)
        # Call the default zone file addition
        self.add_to_default_zones()

    # ####################################
    # Utility Methods
    # ####################################

    # Create an intermediate file to warehouse the normalized config
    def normalize_contents(self):
        if os.path.exists(self.zonefile):
            rando = self.id_generator(8)
            rando_filepath = "/tmp/%s" % rando
            subprocess.call(['named-checkzone', '-o', rando_filepath,
                             self.domain, self.zonefile])
            logging.info('created temporary file %s' % rando_filepath)
            return rando_filepath

    def has_zone(self):
        if os.path.exists('/etc/bind/db.%s' % self.domain):
            return True
        return False

    def id_generator(self, size=6):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    # #######################################
    # Parsing Array to Zone Dictionary - this is going
    # to be a bit messy, and specific to loading
    # from the named-checkzone utility - this is brittle
    # #######################################

    def sanity(self, data, esize=5):
            if len(data) < esize:
                raise IndexError("Array Notation should conform to "
                                 "named-checkzone specification")

    def update_a(self, data):
        self.zone.a(data)

    def a_from_array(self, data):
        self.sanity(data, 4)
        data = trim(data)
        print(data)
        ttl = data[1].strip().split(' IN')[0]
        addr = data[-1].strip()
        try:
            if len(data[0].split('.')) > 1:
                alias = str(self.tldxtr(data[0].strip()).subdomain)
            else:
                alias = data[0]
        except:
            alias = "@"
        if alias == "":
            alias = "@"
        parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        self.zone.a(parsed)

    def update_cname(self, data):
        self.zone.cname(data)

    def cname_from_array(self, data):
        self.sanity(data)

        alias = self.tldxtr(data[0]).subdomain
        ttl = data[1]
        addr = data[4].strip()
        parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        self.zone.cname(parsed)

    def update_ns(self, data):
        self.zone.ns(data)

    def ns_from_array(self, data):
        self.sanity(data)

        ttl = data[1]
        addr = data[4]
        alias = data[0]
        if not alias:
            alias = "@"

        parsed = {'ttl': ttl, 'alias': alias, 'addr': addr}
        self.zone.ns(parsed)

    def naptr_from_array(self, data):
        self.sanity(data)
        alias = data[0]
        order = data[4]
        pref = data[5]
        flag = data[6]
        params = data[7]
        regexp = data[8]
        replace = data[9]
        parsed = {'alias': alias, 'order': order, 'pref': pref, 'flag': flag,
                  'params': params, 'regexp': regexp, 'replace': replace}
        self.zone.naptr(parsed)

    def srv_from_array(self, data):
        self.sanity(data)
        alias = data[0]
        priority = data[4]
        weight = data[5]
        port = data[6]
        target = data[7]
        parsed = {'alias': alias, 'priority': priority, 'weight': weight,
                  'port': port, 'target': target}
        self.zone.srv(parsed)

    def update_soa(self, data):
        self.zone.soa(data)

    def soa_from_array(self, data):
        self.sanity(data)

        logging.info("data: %s" % data)
        # root 0
        ttl = data[1]
        # ttl 2
        # rr 3
        addr = data[4]
        owner = data[5]
        serial = data[6]
        refresh = data[7]

        try:
            update_retry = data[8]
        except:
            update_retry = None
        try:
            expiry = data[9]
        except:
            expiry = None
        try:
            minimum = data[10]
        except:
            minimum = None
        parsed = {'ttl': ttl, 'addr': addr, 'owner': owner, 'serial': serial,
                  'refresh': refresh, 'update-retry': update_retry,
                  'expiry': expiry, 'minimum': minimum}
        self.zone.soa(parsed)

    def array_to_zone(self, blob=None):
        if not blob:
            blob = self.contents

        for entry in blob:
            line = entry.split()
            rrtype = self.find_type(line)
            dclass = line[rrtype].strip()
            for case in switch(dclass):
                if case('AAAA'):
                    self.aaaa_from_array(line)
                    break
                if case('CNAME'):
                    self.cname_from_array(line)
                    break
                if case('NS'):
                    self.ns_from_array(line)
                    break
                if case('NAPTR'):
                    self.naptr_from_array(line)
                    break
                if case('SOA'):
                    self.soa_from_array(line)
                    break
                if case('SRV'):
                    self.srv_from_array(line)
                    break
                if case('A'):
                    self.a_from_array(line)
                    break
                if case():
                    pass
                    logging.warning('Unable to match type %s' % dclass)

    # This may get slow
    def find_type(self, line):
        for t in self.implemented_records:
            if t.upper() in line:
                return line.index(t.upper())
        return -1

    # Somewhat ambiguous. array_to_zone parses a full array to populate
    # dict to zone assumes a single record.
    def dict_to_zone(self, record):
        if 'rr' in record.keys():
            for case in switch(record['rr']):
                if case('NS'):
                    self.update_ns(record)
                    break
                if case('SOA'):
                    self.update_soa(record)
                    break
                if case('CNAME'):
                    self.update_cname(record)
                    break
                if case('A'):
                    self.update_a(record)
                    break
                if case():
                    pass
                    logging.warning('Unable to match type %s' % record['rr'])

    # #######
    # Default Zone Config File Maintenance
    # #######

    def add_to_default_zones(self):
        zones = self.read_default_zones()
        if self.exists_in_default_zones(zones) != -1:
            logging.info("Zone found, returning")
            return
        addition = ['zone "%s" {' % self.domain,
                    '    type master;',
                    '    file "%s";' % self.zonefile,
                    "};"
                    ""]
        self.write_default_zones(addition)
        # Tell bind to refresh zone configuration

    def exists_in_default_zones(self, zones):
        logging.info("Searching for %s" % self.domain)
        for idx, val in enumerate(zones):
            if self.domain in val:
                return idx
        return -1

    def read_default_zones(self):
        with open('/etc/bind/named.conf.default-zones') as f:
            default_zones = f.readlines()
        return default_zones

    def write_default_zones(self, config):
        with open('/etc/bind/named.conf.default-zones', 'a') as f:
            f.write('\n'.join(config))


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
