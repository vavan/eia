#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time

class Form(BaseClientForm):
           

    def show_client_ips(self, uid):
        addresses = self.db.get_client_addresses(uid)
        iplist = map(lambda x: x[1], addresses)
        out = '; '.join(iplist)
        return out

    def show(self):
        text = self.text
        r = self.r
        
        db = self.db
        client = db.get_client(self.login)
        r.ipaddr = self.show_client_ips(self.login)
        r.traf = "%.2f"%float(client.traf.traf)
        r.account = "%.2f"%float(client.account - client.acctlimit)
        r.debt = "%.2f"%float(abs(client.acctlimit))
              
        if client.traf.limit == '0':
            r.traflimit = 'No'
        else:
            r.traflimit = client.traf.limit
        
        if client.traf.traf > client.traf.limit:
            r.traf_color = "#FF0000"
        else:
            r.traf_color = "#FFFFFF"
        
        r.model = client.rate.get_name(self.text)
      
        f = file("template/client_main.html")
        html = f.read()
        return html
    

    def process(self):
        if self.form.has_key("set_traflimit") and self.form.has_key("traflimit"):
            traflimit = self.getvalue("traflimit", int)
            self.db.set_traflimit(self.login, traflimit)
        return self.show()
    

Form().run()

