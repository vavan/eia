#!/usr/bin/python

import sys, os
from datetime import timedelta
from sql_db import DataBase
from request import Time
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config


config.init_log()
db = DataBase(config.sql_credentials)

t = Time()
time_range = t.period( timedelta(minutes = config.period) )

time_n_load = db.get_log(time_range, is_outgoing = True)
if len(time_n_load) == 2:
    delta = t.create(time_n_load[1][0]) - t.create(time_n_load[0][0])
    load = float(time_n_load[1][1]) * 8 * 1000 * 1000 / delta.seconds
    print '%d'%int(round(load))
    print 3000
else:
    print 5000
    print 3000
    
    
    