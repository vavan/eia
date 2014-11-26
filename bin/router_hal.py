import logging
import router 


class RouterHal:
    def __init__(self, db):
        self.db = db
        self.router = router.Router()

    def get(self):
        return dict(self.db.get_cache())
        
    def refresh_ip(self):
        address_map = self.router.address_map()
        for ip, mac in address_map:
            self.db.update_device_ip(mac, ip)
        
    def block(self, device):
        logging.debug("Block device: %s"%device)
        device = self.db.get_device(device)
        self.router.add(device.mac)
        self.db.add_cache(device.id)

    def allow(self, device):
        logging.debug("UnBlock device: %s"%device)
        device = self.db.get_device(device)
        self.router.remove(device.mac)
        self.db.delete_cache(device.id)


