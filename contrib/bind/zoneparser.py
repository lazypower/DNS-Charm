import datetime
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

from common import (
    return_sub as sub,
    trim_empty_array_elements as trim,
)


# Note about how this is constructed. BIND ships with a tool called
# named-checkzone. This normalizes ALL output from a bind file, and
# allows this class to make some assumptions about placement of values.
# Anything loaded from file here will be passed through this utility.
# If it fails to noujrmalize/parse the file, then the operation will fail.

# I'm open to suggestions on how to do this outside of relying on bind's
# wrapping normalizer

logging.basicConfig(level=logging.INFO)


class ZoneParser(object):

    def __init__(self, domain, file_handle=None):
        self.zone = Zone()
        self.domain = domain
        self.zonefile = "/etc/bind/db.%s" % self.domain
        self.implemented_records = self.zone.contents.keys()
        if self.has_zone():
            self.load_and_parse('/etc/bind/db.%s' % self.domain)

    def load_and_parse(self, filepath):
        self.contents = self.from_file()
        self.array_to_zone()

    def from_file(self):
        contents = []
        if self.has_zone():
            self.backup()
            with open(self.zonefile, 'r') as f:
                for line in f.readlines():
                    # ignore comments
                    if not line.begins_with(';'):
                        contents.append(line)
        return contents

    def save(self):
        self.zone.to_file(self.zonefile)
        # Call the default zone file addition
        self.add_to_local_zones()

    # ####################################
    # Utility Methods
    # ####################################

    def backup(self, fmt='%Y-%m-%d-%H-%M-%S_{zone}'):
        if self.has_zone():
            zf = self.zonefile
            with open(zf) as f:
                of = f.read()
            tsf = datetime.datetime.now().strftime(fmt).format(zone=zf)
            with open(tsf, 'w') as outf:
                outf.write(of)

    def passes_validation(self):
        if not self.has_zone():
            raise IOError("Zone file not found %s" % self.zonefile)

        ret = subprocess.call(['named-checkzone', self.domain, self.zonefile])
        if not ret == 0:
            return False
        return True

    def has_zone(self):
        if os.path.exists('/etc/bind/db.%s' % self.domain):
            return True
        return False

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    # def id_generator(self, size=6):
    #     chars = string.ascii_uppercase + string.digits
    #     return ''.join(random.choice(chars) for _ in range(size))

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
        data = trim(data)
        self.sanity(data, 4)
        addr = data[-1].strip()

        # If position 1 is numeric, its a TTL
        if self.is_number(data[1]):
            ttl = data[1]

        if len(data[0].split('.')) > 1:
            alias = sub(self.domain, data[0])
        else:
            alias = data[0]

        try:
            parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        except:
            parsed = {'addr': addr, 'alias': alias}
        self.zone.a(parsed)

    def update_cname(self, data):
        self.zone.cname(data)

    def cname_from_array(self, data):
        logging.info("CNAME data: %s" % data)
        self.sanity(data, 4)
        alias = sub(self.domain, data[0])
        # CNAME's can have TTLS or use the global
        if len(data) > 4:
            ttl = data[2]
            addr = data[4].strip()
        else:
            addr = data[3].strip()
        try:
            parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        except:
            parsed = {'addr': addr, 'alias': alias}

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

    # see tests/fixtures/db.orangebox.com for expected format.
    # As this is handled by the Jinja template, it shouldn't change much.
    def soa_from_array(self, data):
        self.sanity(data)
        logging.info("SOA data: %s" % data)
        addr = data[3]
        owner = data[4]
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
        parsed = {'addr': addr, 'owner': owner, 'serial': serial,
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

    def add_to_local_zones(self):
        zones = self.read_local_zones()
        if self.exists_in_local_zones(zones) != -1:
            logging.info("Zone found, returning")
            return
        addition = ['zone "%s" {' % self.domain,
                    '    type master;',
                    '    file "%s";' % self.zonefile,
                    "};"
                    ""]
        self.write_local_zones(addition)
        # Tell bind to refresh zone configuration

    def exists_in_local_zones(self, zones):
        logging.info("Searching for %s" % self.domain)
        for idx, val in enumerate(zones):
            if self.domain in val:
                return idx
        return -1

    def read_local_zones(self):
        with open('/etc/bind/named.conf.local-zones') as f:
            default_zones = f.readlines()
        return default_zones

    def write_local_zones(self, config):
        with open('/etc/bind/named.conf.local-zones', 'a') as f:
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
