import logging
import router 


class RouterHal:
    def __init__(self, db):
        self.db = db
        self.cache = dict(self.db.get_cache())
        self.router = router.Router()

    def get(self):
        return self.cache.keys()
        
    def refresh_ip(self):
        for ip, mac in self.router.get_map():
            self.update_device_ip(mac, ip)
        
    def add(self, device):
        logging.debug("Block device: %s"%device)
        device = self.db.get_device(device)
        self.cache[device] = device.mac
        #self.router.add(device.mac)
        self.db.add_cache(device.id)

    def remove(self, device):
        logging.debug("UnBlock device: %s"%device)
        device = self.db.get_device(device)
        del self.cache[device.id]
        #self.router.remove(device.mac)
        self.db.delete_cache(device.id)
        #self.refresh_ip()


