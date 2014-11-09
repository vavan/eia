#!/usr/bin/python

import sys, os
from datetime import datetime, timedelta
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time

class Form(BaseClientForm):

    def show_debits(self):
        start, stop = Time().current_day()
        start -= timedelta(days = 30)
        
        self.odd(0)
        body = ''
        total_money = 0
        total_traf = 0
        traf_debit_time  = self.db.get_debit_history(self.login, (start, stop))
        
        for traf, debit, time in traf_debit_time:
            total_traf += traf
            total_money += debit
            body += '<tr %s>'%self.odd()
            body += '<td class="first">%s</td><td>%.1f</td><td>%.2f</td></tr>\n'%( time, traf, debit )
            
        body += '<tr class="bottom">'
        body += '<td class="first">TOTAL</td><td>%.1f</td><td>%.2f</td></tr>\n'%(total_traf, total_money)
        return body
 
    def process(self):
        self.r.debit_list = self.show_debits()
    
        f = file("template/client_debit.html")
        html = f.read()
        return html    

Form().run()

