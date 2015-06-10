import os
from random import randint
from charmhelpers.core.hookenv import unit_get
from charmhelpers.core.host import service_reload

from zoneparser import ZoneParser

from common import resolve_hostname_to_ip


class Provider(object):

    def config_changed(self, domain='example.com'):
        zp = ZoneParser(domain)
        # Install a skeleton bind zone, rehashes existing file
        # if it has contents)
        if not os.path.exists('/etc/bind/db.%s' % domain):
            self.first_setup(zp, domain)
            zp.save()
            self.reload_config()

    def add_record(self, record, domain='example.com'):
        zp = ZoneParser(domain)
        if type(record) is dict:
            zp.dict_to_zone(record)
        elif type(record) is list:
            zp.array_to_zone(record)
        else:
            raise TypeError("Unsupported type for resource %d" % type(record))
        zp.save()
        self.reload_config()

    def remove_record(self, record, domain='example.com'):
        zp = ZoneParser(domain)
        if type(record) is dict:
            zp.zone.remove('alias', record['rr'], record['alias'])
        elif type(record) is list:
            for item in record:
                rcrd = item.split(' ')
                try:
                    zp.zone.remove('alias', rcrd[3], rcrd[0])
                except KeyError as e:
                    # skip removals if we dont find the data. log it and move on
                    print "Unable to locate {}".format(rcrd[0])

        zp.save()
        self.reload_config()

    def first_setup(self, parser, domain='example.com'):
        # Insert SOA and NS records
        hostname = unit_get('public-address')
        addr = resolve_hostname_to_ip(hostname)
        parser.dict_to_zone({'rr': 'SOA',
                             'addr': 'ns.%s.' % domain,
                             'owner': 'root.%s.' % domain,
                             'serial': randint(12345678, 22345678),
                             'refresh': '12h',
                             'update-retry': '15m',
                             'expiry': '3w',
                             'minimum': '3h'})
        parser.dict_to_zone({'rr': 'NS', 'alias': '@', 'ttl': 1600,
                             'addr': 'ns.%s.' % domain})
        parser.dict_to_zone({'rr': 'A', 'alias': 'ns', 'addr': addr,
                             'ttl': 300})

    def reload_config(self):
        service_reload('bind9')
