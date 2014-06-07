import datetime
import logging
import os
import subprocess
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
                    if not line.startswith(';') and not line.startswith('$'):
                        contents.append(line)
        return contents

    def save(self):
        proposed = "{zone}.proposed".format(zone=self.zonefile)
        # write the output to a proposed file
        self.zone.to_file(proposed)
        # perform sanity check on proposed zone
        if self.passes_validation(proposed):
            logging.info('Zone additions accepted. writing to ZoneFile')
            self.zone.to_file(self.zonefile)
            os.remove(proposed)
        else:
            raise Exception('Check failing dirty zone file %s' % proposed)

        # Call the default zone file addition
        self.add_to_local_zones()

    # ####################################
    # Utility Methods
    # ####################################

    def backup(self, fmt='%Y-%m-%d-%H-%M-%S_{zone}'):
        if self.has_zone():
            with open(self.zonefile) as f:
                of = f.read()
            zf = datetime.datetime.now().strftime(fmt).format(zone=self.domain)
            with open('/etc/bind/zone-backup/%s' % zf, 'w') as outf:
                outf.write(of)

    def passes_validation(self, zf=None):
        # Must be first setup - slime the return value.
        if not self.has_zone():
            return True

        if not zf:
            zf = self.zonefile

        ret = subprocess.call(['named-checkzone', self.domain, zf])
        logging.info('RET Code: %s' % ret)
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

    # This may get slow
    def find_type(self, line):
        for t in self.implemented_records:
            if t.upper() in line:
                return line.index(t.upper())
        return -1

    def sanity(self, data, esize=5):
        if len(data) < esize:
            raise IndexError("Array Notation should conform to "
                             "specification in docs/relations.md")

    # #######################################
    # Parsing Array to Zone Dictionary - this is going
    # to be a bit messy, and specific to loading
    # from the named-checkzone utility - this is brittle
    # #######################################

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
        if self.is_number(data[1]):
            ttl = data[1]
        addr = data[-1].strip()

        try:
            parsed = {'ttl': ttl, 'addr': addr, 'alias': alias}
        except:
            parsed = {'addr': addr, 'alias': alias}

        self.zone.cname(parsed)

    def update_ns(self, data):
        self.zone.ns(data)

    def ns_from_array(self, data):
        self.sanity(data, 4)

        alias = data[0]
        addr = data[-1].strip()
        if self.is_number(data[1]):
            ttl = data[1]

        try:
            parsed = {'ttl': ttl, 'alias': alias, 'addr': addr}
        except:
            parsed = {'alias': alias, 'addr': addr}
        self.zone.ns(parsed)

    def naptr_from_array(self, data):
        self.sanity(data)
        alias = data[0]
        if self.is_number(data[1]):
            ttl = data[1]
        order = data[-6]
        pref = data[-5]
        flag = data[-4]
        params = data[-3]
        regexp = data[-2]
        replace = data[-1].strip()
        try:
            parsed = {'alias': alias, 'order': order, 'pref': pref,
                      'flag': flag, 'params': params, 'regexp': regexp,
                      'replace': replace, 'ttl': ttl}
        except:
            parsed = {'alias': alias, 'order': order, 'pref': pref,
                      'flag': flag, 'params': params, 'regexp': regexp,
                      'replace': replace}
        self.zone.naptr(parsed)

    def srv_from_array(self, data):
        self.sanity(data)
        alias = data[0]
        if self.is_number(data[1]):
            ttl = data[1]
        priority = data[-4]
        weight = data[-3]
        port = data[-2]
        target = data[-1].strip()
        try:
            parsed = {'alias': alias, 'priority': priority, 'weight': weight,
                      'port': port, 'target': target, 'ttl': ttl}
        except:
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

        blob = trim(blob)

        methods = {'A': self.a_from_array,
                   'CNAME': self.cname_from_array,
                   'NS': self.ns_from_array,
                   'NAPTR': self.naptr_from_array,
                   'SOA': self.soa_from_array,
                   'SRV': self.srv_from_array}

        logging.info('Processing records from: %s' % blob)
        for entry in blob:
            line = entry.split()
            rrtype = self.find_type(line)
            dclass = line[rrtype].strip()
            try:
                methods[dclass](line)
            except:
                logging.info('Failed to locate method for parsing %s' % dclass)

    # Array_to_zone parses a full array to populate dict to zone
    # assumes a single record.
    def dict_to_zone(self, record):
        methods = {'A': self.update_a,
                   'CNAME': self.update_cname,
                   'SOA': self.update_soa,
                   'NS': self.update_ns}
        if 'rr' in record.keys():
            try:
                methods[record['rr']](record)
            except:
                logging.info('Failed to locate method for %s' % record['rr'])

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
        with open('/etc/bind/named.conf.local') as f:
            default_zones = f.readlines()
        return default_zones

    def write_local_zones(self, config):
        with open('/etc/bind/named.conf.local', 'a') as f:
            f.write('\n'.join(config))
