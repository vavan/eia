import logging
import router 


class RouterHal:
    def __init__(self, db):
        self.db = db
        self.list = map(lambda x: x[0], self.db.get_cache())
        self.router = router.Router()

    def get(self):
        return self.list

    def add(self, mac):
        logging.debug("Block device: %s"%mac)
        self.list.append(mac)
        self.router.add(mac)
        self.db.add_cache(mac

    def remove(self, mac):
        logging.debug("UnBlock device: %s"%mac)
        self.list.remove(mac)
        self.router.remove(mac)
        self.db.delete_cache(mac)


