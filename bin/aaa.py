#!/usr/bin/python

import os, sys, re
from collections import defaultdict
import traceback, StringIO, logging
import datetime
import sets

sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config
from sql_db import DataBase
from router_hal import RouterHal

class AAA:
    MEG = 1000.0*1000.0

    def __init__(self):
        logging.info( "Start AAA")
        self.db = DataBase(config.sql)

    def get_planned(self):
        alive = map(lambda x: x[0], self.db.get_alives())
        all = map(lambda x: x.id, self.db.get_devices())
        alive = set(alive)
        all = set(all)
        return all - alive

    def main(self):
        self.db.expire_alive()
        hal = RouterHal(self.db)
        actual = set(hal.get())
        planned = self.get_planned()

        new = planned - actual
        old = actual - planned
        for i in new:
            hal.add(i)
        for i in old:
            hal.remove(i)


def log_except(exc):
    stream = StringIO.StringIO()
    traceback.print_exception(getattr(exc,"__class__"), exc, sys.exc_traceback, None, stream)
    logging.error(stream.getvalue())

if __name__ == '__main__':
    config.init_log()
    try:
        AAA().main()
    except Exception, e:
        logging.error( 'Unhandled exception in AAA:' )
        log_except( e )
