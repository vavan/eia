import logging
import router 


class RouterHal:
    def __init__(self, db):
        self.db = db
        self.router = router.Router()
        self.cache = dict(self.db.get_cache())

    def get(self):
        return self.cache
        
    def refresh_ip(self):
        macs = self.db.get_devices_empty_ip()
        if len(macs) > 0:
            address_map = self.router.address_map()
            for ip, mac in address_map:
                if mac in macs:
                    self.db.update_device_ip(mac, ip)
        
    def block(self, device):
        logging.debug("Block device: %s"%device)
        if device not in self.cache:
            device = self.db.get_device(device)
            self.db.add_cache(device.id)
            self.router.add(device.mac)

    def allow(self, device):
        logging.debug("UnBlock device: %s"%device)
        if device in self.cache:
            device = self.db.get_device(device)
            self.db.delete_cache(device.id)
            self.router.remove(device.mac)


