import logging

class RouterHal:
    def __init__(self, db):
        self.pulled = False
        self.pushed = False
        self.db = db
        self.list = map(lambda x: x[0], self.db.get_cache())

    def get(self):
        return self.list

    def pull(self):
        if not self.pulled:
            #pull from hardware
            self.pulled = True

    def apply(self):
        if self.pushed:
            self.db.update_cache(self.list)

    def add(self, mac):
        self.pushed = True
        self.pull()
        self.list.append(mac)
        logging.debug("Block device: %s"%mac)
        #push add-'mac' to hardware

    def remove(self, mac):
        self.pushed = True
        self.pull()
        self.list.remove(mac)
        logging.debug("UnBlock device: %s"%mac)
        #push del-'mac' to hardware


import urllib
params = urllib.urlencode({'username': 'admin', 'password': 'dostup3369'})
f = urllib.urlopen("http://10.0.0.1", params)
print f.read()

