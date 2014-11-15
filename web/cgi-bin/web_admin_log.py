#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseAdminForm, Calendar
from request import Time



class AdminLog(BaseAdminForm):
        
    def collect_netload(self, time_range):
        time_n_lan = self.db.get_log(time_range)
        time_n_wan = self.db.get_log(time_range, is_outgoing = True)
        time_n_wan = dict( time_n_wan )
        time_n_load = []
        for when, lan in time_n_lan:
            if when in time_n_wan:
                wan = time_n_wan[when]
            else:
                wan = '0'
            time_n_load.append( [when, lan, wan] )
        return time_n_load
        

    def process_netload(self, time_n_load):
        t = Time()
        prev = t.create(time_n_load[0][0]) - datetime.timedelta(minutes = 10)
        for i in time_n_load:
            when, lan, wan = i
            when = t.create(when)
            delta = when - prev
            prev = when
            i[0] = t.str(when)[:-3]
            i[1] = float(lan) * 8000 / delta.seconds
            i[2] = float(wan) * 8000 / delta.seconds
        return time_n_load
    
    def show_network_load(self, time_range):
        time_n_load = self.collect_netload(time_range)
        time_n_load = self.process_netload(time_n_load)
        
        body = ''
        index = 0
        for when, load_lan, load_wan  in time_n_load:
            index += 1
            body += '<tr %s>'%self.odd(index)
            if load_lan > 4000:
                body += "<td><b>%s</b></td><td>%.1f</td><td>%.1f</td>"%( when, load_lan, load_wan )
            else:
                body += "<td>%s</td><td>%.1f</td><td>%.1f</td>"%( when, load_lan, load_wan )
        return body

    def process(self):
        c = Calendar(self.f)
        time_range = c.get_time_range()

        self.r.select_month = c.select_month()            
        self.r.network_load = self.show_network_load(time_range)
        
        f = file("log.html")
        html = f.read()
        return html


AdminLog().run()