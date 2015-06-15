from common import provider_keys
from boto import route53

class Provider:

    # Primary Interface Methods
    ALLOWED_RECORDS = ['A', 'CNAME', 'NS', 'SRV']


    def __init__(self, domain, key=None, secret=None):
        if not key or not secret:
            pkey = provider_keys()
            key = pkey['AWS_ACCESS_KEY_ID']
            secret = pkey['AWS_SECRET_ACCESS_KEY']

        self.connection = route53.connection.Route53Connection(
                aws_access_key_id=key,
                aws_secret_access_key=secret)
        self.domain = domain
        self.zone = self.connection.get_zone("{}.".format(self.domain))


    def config_changed(self):
        if not self.zone.id:
            raise ValueError("Missing ZoneID for Domain. Is domain declared"
                             " in AWS Route53?")


    def add_record(self, record):
        if type(record) is dict:
           # single record
           self.parse_record(record)
        if type(record) is list:
            for r in record:
                self.parse_record(record)


    def remove_record(self):
        """
        Used to remove an entry from a zone
        """
        pass


    def update_record(self):
        """
        Used to update an entry in a zone
        """
        pass

    # Supporting Methods
    def parse_record(self, entry):
         methods = {'A': self.create_a_record,
                   'CNAME': self.create_cname_record,
                   'NS': self.create_ns_record,
                   'SRV': self.create_srv_record,}

         if 'rr' in entry.keys():
            methods[entry['rr']](entry)
         else:
             raise ValueError("Missing record type - see README for accepted"
                              " dns record types")



    def create_a_record(self, record):
        """
        takes params: (str)name, (str)values, (str)ttl
        """
        zone = self.connection.get_hozed_zone_by_id(get_zone_id(self.domain))
        new_record, change_info = zone.create_a_record(name=record['name'],
                                        values=record['addr'],
                                        ttl=record['ttl']
        )

    def create_cname_record(self, record):
        """
        takes params: (str)name, (str)values, (str)ttl
        """
        pass

    def create_ns_record(self, record):
        """
        takes params: (str)name, (str)values, (str)ttl
        """
        pass

    def create_srv_record(self, record):
        """
        takes params: (str)name, (str)values, (str)ttl
        """
        pass


