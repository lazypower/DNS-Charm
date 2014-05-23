from .zone import Zone


class ZoneParser(object):

    def __init__(self, file_handle=None):
        if file_handle:
            self.contents = self.from_file(file_handle)
        self.zone = Zone()
        self.implemented_records = self.zone.contents.keys()

    def from_file(self, file_handle):
        contents = []
        with open(file_handle) as f:
            for line in f.readlines():
                contents.append(line)
        return contents

    def from_dict(self, dns_records):
        self.__validate_attributes(dns_records)

    def __validate_attributes(self, configuration):
            if configuration['type'] not in self.implemented_records:
                raise KeyError("Unknown key %s" % configuration['type'])
