from . import zone


class ZoneParser(object):

    def __init__(self, file_handle=None):
        if file_handle:
            self.contents = self.from_file(file_handle)
            self.zone = zone()

    def from_file(self, file_handle):
        contents = []
        with open(file_handle) as f:
            for line in f.readlines():
                contents.append(line)
        return contents

    def from_dict(self, dns_records):
        if not self.__validate_attributes():
            raise KeyError("Failed to locate all necessary attributes")

    def __validate_attributes(self, configuration):
        for key in configuration.iteritems():
            print key
