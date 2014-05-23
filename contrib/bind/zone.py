
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

    def aaaa(self, value=None):
        if not value:
            return self.contents['aaaa']
        else:
            self.contents['aaaa'].append(value)
            return self.contents['aaaa']

    def caa(self, value=None):
        if not value:
            return self.contents['caa']
        else:
            self.contents['caa'].append(value)
            return self.contents['caa']

    def cert(self, value=None):
        if not value:
            return self.contents['cert']
        else:
            self.contents['cert'].append(value)
            return self.contents['cert']

    def cname(self, value=None):
        if not value:
            return self.contents['cname']
        else:
            self.contents['cname'].append(value)
            return self.contents['cname']

    def ns(self, value=None):
        if not value:
            return self.contents['ns']
        else:
            self.contents['ns'].append(value)
            return self.contents['ns']

    def ptr(self, value=None):
        if not value:
            return self.contents['ptr']
        else:
            self.contents['ptr'].append(value)
            return self.contents['ptr']

    def soa(self, value=None):
        if not value:
            return self.contents['soa']
        else:
            self.contents['soa'].append(value)
            return self.contents['soa']

    def spf(self, value=None):
        if not value:
            return self.contents['spf']
        else:
            self.contents['spf'].append(value)
            return self.contents['spf']

    def srv(self, value=None):
        if not value:
            return self.contents['srv']
        else:
            self.contents['srv'].append(value)
            return self.conents['srv']

    def txt(self, value=None):
        if not value:
            return self.contents['txt']
        else:
            self.contents['txt'].append(value)
            return self.contents['txt']
