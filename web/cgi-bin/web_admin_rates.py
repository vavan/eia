#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from main import Rate
from web_base import BaseAdminForm


class AdminRates(BaseAdminForm):
     
    def do_add_rate(self):
        price = self.getvalue('price', float)
        rate_mode = self.getvalue('rate')
        if rate_mode == "model_month":
            mode = Rate.MONTHLY
        elif rate_mode == "model_day":
            mode = Rate.DAILY
        elif rate_mode == "model_minutes":
            mode = Rate.MINUTELY
        else:
            mode = Rate.TRAFBASED
        self.db.add_rate(price, mode)
       
    def show(self):
        out = ''
        rates = self.db.get_rates()
        self.odd(0)
        for rate in rates:
            out += '<tr %s>'%self.odd()
            out += '<td class="first"><a href="web_admin_rates.py?$session_link&delete=%s">Delete</a></td>'%rate.id
            out += '<td>%s</td>'%rate.price
            out += '<td>%s</td>'%rate.get_name(self.text)
            out += '</tr>\n'
        return out
    
    def delete_rate(self, rate_id):
        clients = self.db.get_peers_by_rate(rate_id)
        msg = None
        if len(clients) > 0:
            msg = map(lambda x: x[0], clients)
            msg = ', '.join(msg)
            msg = '$RATE_ERROR1 [%s]. $RATE_ERROR2'%msg
        elif int(rate_id) == Rate.ALLWAYS_EXIST:
            msg = '$RATE_ALLWAYS_EXIST'
        if msg:
            logging.info('Unable to delete rate [%s]'%rate_id)
            self.on_fail(msg, redirect_to = 'web_admin_rates.py?$session_link')
            sys.exit(0)
        else:
            self.db.delete_rate(rate_id)
        

    def process(self):
        if 'add' in self.f:
            self.do_add_rate()
        elif 'delete' in self.f:
            record_id = self.getvalue("delete", int)
            self.delete_rate(record_id)
    

        self.r.rates = self.show()
        
        f = file("template/admin_rates.html")
        html = f.read()
        return html

AdminRates().run()