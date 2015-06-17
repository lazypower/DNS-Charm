#!/usr/bin/env python
import subprocess
try:
    import consul
except:
    subprocess.call(['pip','install','python-consul'])
    import consul
from common import serialize_data, unserialize_data


class ConsulClient():

    def __init__(self, host, port=8500, filepath=None):
        # provide filepath to load from pickled data
        if filepath:
            data = unserialize_data('data/consul-host.json')
            self.host = data['host']
            self.port = data['port']
        self.host = host
        self.port = port
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

