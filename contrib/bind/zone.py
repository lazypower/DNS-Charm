
class Zone(object):

    # Supports an incomplete SPEC of DNS Zones
    def __init__(self):
        self.contents = {
            'a':  [],
            'aaaa': [],
            'caa': [],
            'cert': [],
            'cname': [],
            'ns': [],
            'ptr': [],
            'soa': [],
            'spf': [],
            'srv': [],
            'txt': []
        }

        def a(self, value=None):
            if not value:
                return self.contents['a']
            else:
                self.contents['a'].append(value)
                return self.contents['a']

        def aaaa(self):
            return self.contents['aaaa']

        def caa(self):
            return self.contents['caa']

        def cert(self):
            return self.contents['cert']

        def cname(self):
            return self.contents['cname']

        def ns(self):
            return self.contents['ns']

        def ptr(self):
            return self.contents['ptr']

        def soa(self):
            return self.contents['soa']

        def spf(self):
            return self.contents['spf']

        def srv(self):
            return self.contents['srv']

        def txt(self):
            return self.contents['txt']
