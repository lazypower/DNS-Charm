from mock import patch, Mock
import pytest
import os

from rt53 import provider
#import rt53

class TestRt53Provider():
    """
    This test suite depends on cloud credentials. You can ideally set them to
    anything. But it's fair to assume that you want actual integration tests
    and you should probably stuff in real credentials then.

    export AWS_ACCESS_KEY
    export AWS_SECRET_ACCESS_KEY

    in your CI environment to ensure these tests dont fail due to cloud creds
    missing and life will be good.
    """

    @classmethod
    def setup_class(cls):
        AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        cls.provider = provider.Provider('example.com', AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)


    def test_zoneid_from_domain(self):
        """
            this is an integration level test until I figure out what to mock
            in the route53 lib
        """
        id = self.provider.get_zone_id('example.com')
        if not os.getenv('RT53DOMAIN_KEY'):
            assert id == "ZD4S1IEWT6LPB"
        else:
            assert id == os.getenv('RT53DOMAIN_KEY')


    def test_config_changed(self):
        with patch('rt53.provider.Provider.get_zone_id') as get:
            self.provider.config_changed()
            get.assert_called_with('example.com')

    def test_add_record_with_dict(self):
        record = {'name': 'test', 'rr': 'A', 'ttl': 1600}
        with patch('rt53.provider.Provider.dict_entry') as de:
            self.provider.add_record(record)
            de.assert_called_with(record)

    @patch('rt53.provider.Provider.create_a_record')
    @patch('rt53.provider.Provider.create_cname_record')
    @patch('rt53.provider.Provider.create_ns_record')
    @patch('rt53.provider.Provider.create_srv_record')
    def test_add_record_with_empty_dict_raises_error(self, amk, cmk, nmk, smk):
        record = {'name': 'test', 'ttl': 1600}
        with  pytest.raises(ValueError):
            self.provider.add_record(record)
            record = {}
            self.provider.add_record(record)
        assert amk.not_called()
        assert cmk.not_called()
        assert nmk.not_called()
        assert smk.not_called()


    def test_create_a_record(self):
        record = {'name': 'test', 'ttl': 1600, 'rr': 'A', 'addr': '127.0.0.1'}
        with patch('route53.hosted_zone.HostedZone.create_a_record') as crm:
            self.provider.create_a_record(record)
            crm.assert_called_with('test', '127.0.0.1', 1600)

    def test_create_cname_record(self):
        pass

    def test_create_ns_record(self):
        pass

    def test_create_srv_record(self):
        pass


