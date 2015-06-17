#!/usr/bin/env python
import subprocess
try:
    import consul
except:
    subprocess.call(['pip','install','python-consul'])
    import consul
from common import serialize_data, unserialize_data


class ConsulClient():

    def __init__(self, host=None, port=8500, filepath=None):
        # provide filepath to load from pickled data
        if filepath:
            data = unserialize_data('data/consul-host.json')
            self.host = data['host']
            self.port = data['port']
        if host:
            self.host = host
        if port:
            self.port = port
        if not self.host:
            raise ValueError("Missing host config, cannot initialize class")
        self.client = consul.Consul(host=self.host)
        self.cache = 'data/consul-data.json'

    def cache_services(self):
        services = self.client.agent.services()

        service_list = unserialize_data(self.cache)
        for service in services:
            svc_name = services[service]['Service']
            svc =   {'name': svc_name,
                     'port' : services[service]['Port'],
                     'address': services[service]['Address']}
            service_list[svc_name] = svc

        serialize_data(self.cache, service_list)
        print "Cached service data to: {}".format(self.cache)
        print service_list
        return service_list

    def cache_host(self):
        serialize_data('data/consul-host.json', {'host': self.host,
                                                 'port': self.port})
        print "Saved host data to: data/consul-host.json"

    def read_services(self):
        return unserialize_data(self.cache)

    def build_dns(self, webhost):
        services = self.read_services()
        all_services = []
        for host in webhost:
            for service in services:
                svc = {'rr': 'A', 'alias': service, 'ttl': 60,
                        'addr': webhost[host]['public-address']}
                all_services.append(svc)
        return all_services

