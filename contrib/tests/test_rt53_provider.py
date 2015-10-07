from mock import patch, Mock
import pytest
import os

from rt53 import provider



class TestRt53Provider():
    """
    This test suite depends on cloud credentials. You can ideally set them to
    anything. But it's fair to assume that you want actual integration tests
    and you should probably stuff in real credentials then.

    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY

    in your CI environment to ensure these tests dont fail due to cloud creds
    missing and life will be good.
    """

    @classmethod
    def setup_class(cls):
        AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        cls.provider = provider.Provider('example.com', AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)

    @pytest.mark.skipif(os.getenv('AWS_ACCESS_KEY_ID') is None,
                        reason="requires credentials")
    @patch('rt53.provider.route53.record.ResourceRecordSets')
    def test_add_record_with_dict(self, rrm):
        record = {'name': 'test', 'rr': 'A', 'ttl': 1600}
        with patch('rt53.provider.Provider.parse_record') as de:
            self.provider.add_record(record)
            de.assert_called_once(record, rrm)

    @patch('rt53.provider.Provider.create_a_record')
    @patch('rt53.provider.Provider.create_cname_record')
    @patch('rt53.provider.Provider.create_ns_record')
    @patch('rt53.provider.Provider.create_srv_record')
    @pytest.mark.skipif(os.getenv('AWS_ACCESS_KEY_ID') is None,
                        reason="requires credentials")
    def test_add_record_with_empty_dict_raises_error(self, amk, cmk, nmk, smk):
        record = {'name': 'test', 'ttl': 1600}
        with pytest.raises(ValueError):
            self.provider.add_record(record)
            record = {}
            self.provider.add_record(record)
        assert amk.not_called()
        assert cmk.not_called()
        assert nmk.not_called()
        assert smk.not_called()

    @pytest.mark.skipif(os.getenv('AWS_ACCESS_KEY_ID') is None,
                        reason="requires credentials")
    def test_create_a_record(self):
        record = {'alias': 'test', 'ttl': 1600, 'rr': 'A', 'addr': '127.0.0.1'}
        with patch('boto.route53.record.ResourceRecordSets') as crm:
            self.provider.create_a_record(record, crm)
            crm.add_change.assert_called_with('UPSERT', 'test.example.com',
                                              'A', ttl=1600)
