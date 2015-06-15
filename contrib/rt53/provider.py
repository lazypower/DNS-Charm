from common import provider_keys
import route53

class Provider:

    # Primary Interface Methods

    def __init__(self, domain, key=None, secret=None):
        if not key or not secret:
            pkey = provider_keys()
            key = pkey['AWS_ACCESS_KEY']
            secret = pkey['AWS_SECRET_KEY']

        self.connection = route53.connect(
                aws_access_key_id=key,
                aws_secret_access_key=secret)
        self.record_types = ['A', 'CNAME', 'NS', 'SRV']
        self.domain = domain
        zone_id = self.get_zone_id(self.domain)
        self.zone = self.connection.get_hosted_zone_by_id(zone_id)


    def config_changed(self):
        zone_id = self.get_zone_id(self.domain)
        if not zone_id:
            raise ValueError("Missing domain in AWS Rt53")


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

    def get_zone_id(self, domain_name="example.com"):
        # i feel like looping is silly, but ok, maybe you
        # have 5k domains and we need to paginate them.
        for zone in self.connection.list_hosted_zones():
            if domain_name in zone.name:
                return zone.id

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


