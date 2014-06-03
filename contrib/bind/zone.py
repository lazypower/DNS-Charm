import jinja2
import os


# Supports an incomplete SPEC of DNS Zone entrys
class Zone(object):
    # TODO: Add Validation
    # TODO: Compare with RFC

    def __init__(self):
        self.contents = {
            'A':  [],
            'AAAA': [],
            'CAA': [],
            'CERT': [],
            'CNAME': [],
            'NAPTR': [],
            'NS': [],
            'PTR': [],
            'SOA': [],
            'SPF': [],
            'SRV': [],
            'TXT': []
        }

    def a(self, value=None):
        if not value:
            return self.contents['A']
        else:
            idx = self.find(self.contents['A'], 'alias', value['alias'])
            if idx != -1:
                self.contents['A'].pop(idx)
            self.contents['A'].append(value)
            return self.contents['A']

    def aaaa(self, value=None):
        if not value:
            return self.contents['AAAA']
        else:
            self.contents['AAAA'].append(value)
            return self.contents['AAAA']

    def caa(self, value=None):
        if not value:
            return self.contents['CAA']
        else:
            self.contents['CAA'].append(value)
            return self.contents['CAA']

    def cert(self, value=None):
        if not value:
            return self.contents['CERT']
        else:
            self.contents['CERT'].append(value)
            return self.contents['CERT']

    def cname(self, value=None):
        if not value:
            return self.contents['CNAME']
        else:
            idx = self.find(self.contents['CNAME'], 'alias', value['alias'])
            if idx != -1:
                self.contents['CNAME'].pop(idx)
            self.contents['CNAME'].append(value)
            return self.contents['CNAME']

    def ns(self, value=None):
        if not value:
            return self.contents['NS']
        else:
            idx = self.find(self.contents['NS'], 'alias', value['alias'])
            if idx != -1:
                self.contents['NS'].pop(idx)
            self.contents['NS'].append(value)
            return self.contents['NS']

    def naptr(self, value=None):
        if not value:
            return self.contents['NAPTR']
        else:
            # idx = self.find(self.contents['NAPTR'], 'alias', value['alias'])
            # if idx != -1:
            #     self.contents['NAPTR'].pop(idx)
            self.contents['NAPTR'].append(value)
            return self.contents['NAPTR']

    def ptr(self, value=None):
        if not value:
            return self.contents['PTR']
        else:
            self.contents['PTR'].append(value)
            return self.contents['PTR']

    def soa(self, value=None):
        if not value:
            return self.contents['SOA']
        else:
            if len(self.contents['SOA']) > 0:
                self.contents['SOA'].pop(-1)
            self.contents['SOA'].append(value)
            return self.contents['SOA']

    def spf(self, value=None):
        if not value:
            return self.contents['SPF']
        else:
            self.contents['SPF'].append(value)
            return self.contents['SPF']

    def srv(self, value=None):
        if not value:
            return self.contents['SRV']
        else:
            self.contents['SRV'].append(value)
            return self.contents['SRV']

    def txt(self, value=None):
        if not value:
            return self.contents['TXT']
        else:
            self.contents['TXT'].append(value)
            return self.contents['TXT']

    # ############
    # Template Methods
    # ############

    def to_file(self, filepath='/etc/bind/db.example.com'):
        contents = self.read_template()
        t = jinja2.Template(contents)

        with open('%s' % filepath, 'w') as f:
            f.write(t.render(data=self.contents))

    def read_template(self):
        with open('%s/contrib/bind/templates/zone.jinja2' %
                  os.environ['CHARM_DIR']) as f:
            return f.read()

    # #############
    # Utility methods
    # #############
    def find(self, lst, key, value):
        for i, dic in enumerate(lst):
            if dic[key] == value:
                return i
        return -1

    def remove(self, needle, haystack, value):
        if not haystack in self.contents.keys():
            raise IndexError("Unable to locate %s in storage" % haystack)
        idx = self.find(self.contents[haystack], needle, value)
        if idx == -1:
            raise KeyError("Value not found in %s" % haystack)
        self.contents[haystack].pop(idx)
