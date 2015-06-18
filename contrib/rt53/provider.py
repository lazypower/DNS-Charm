from common import provider_keys
from boto import route53

class Provider:

    # Primary Interface Methods
    ALLOWED_RECORDS = ['A', 'CNAME', 'NS', 'SRV', 'NAPTR']


    def __init__(self, domain, key=None, secret=None):
        if not key or not secret:
            pkey = provider_keys()
            key = pkey['AWS_ACCESS_KEY_ID']
            secret = pkey['AWS_SECRET_ACCESS_KEY']

        self.client = route53.connection.Route53Connection(
                aws_access_key_id=key,
                aws_secret_access_key=secret)
        self.domain = domain
        self.zone = self.client.get_zone("{}.".format(self.domain))

    def config_changed(self):
        if not self.zone.id:
            raise ValueError("Missing ZoneID for Domain. Is domain declared"
                             " in AWS Route53?")


    def add_record(self, record):
        resource = route53.record.ResourceRecordSets(self.client, self.zone.id)
        if type(record) is dict:
           # single record
           self.parse_record(record, resource)
        if type(record) is list:
            for r in record:
                self.parse_record(r, resource)


    def remove_record(self, record):
        """
        Used to remove an entry from a zone
        """
        pass


    def update_record(self, record):
        resource = route53.record.ResourceRecordSets(self.client, self.zone.id)
        if type(record) is dict:
           # single record
           self.parse_record(record, resource)
        if type(record) is list:
            for r in record:
                self.parse_record(r, resource)

    # Supporting Methods
    def parse_record(self, entry, resource):
         methods = {'A': self.create_a_record,
                   'CNAME': self.create_cname_record,
                   'NS': self.create_ns_record,
                   'SRV': self.create_srv_record,
                   'NAPTR': self.create_naptr_record,}

         if 'rr' in entry.keys():
            methods[entry['rr']](entry, resource)
         else:
             raise ValueError("Missing record type - see README for accepted"
                              " dns record types")



    def create_a_record(self, record, resource):
        print record
        fqdn = "{}.{}".format(record['alias'], self.domain)
        if "ttl" in record.keys() and record['ttl']:
            status = resource.add_change("UPSERT", fqdn, "A", ttl=record['ttl'])
        else:
            status = resource.add_change("UPSERT", fqdn, "A")
        status.add_value(record['addr'])
        resource.commit()

    def create_naptr_record(self, record, resource):
        print "Rt53  Does not yet support NAPTR resources"

    def create_cname_record(self, record, resource):
        fqdn = "{}.{}".format(record['alias'], self.domain)
        if "ttl" in record.keys() and record['ttl']:
            status = resource.add_change("UPSERT", fqdn, "CNAME", ttl=record['ttl'])
        else:
            status = resource.add_change("UPSERT", fqdn, "CNAME")
        status.add_value(record['addr'])
        resource.commit()


    def create_ns_record(self, record, resource):
        print "NS Records Not Implemented"

    def create_srv_record(self, record, resource):
        print "SRV records not implemented"



