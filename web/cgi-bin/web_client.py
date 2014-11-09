#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseForm
from request import Time

class Form(BaseForm):
        
    def is_admin(self):
        return False
    
    def show_messages(self, messages):
        out = ''
        if messages:
            for when, what in messages:
                out += '<tr height="30">'
                out += '<td colspan=2>'
                out += '<div style="font-weight: bold;background-color:#FFFDC9">%s</div>'%when
                out += '%s'%what
                out += '</td></tr>'
        return out

    def show(self):
        text = self.text
        r = self.r
        
        db = self.db
        client = db.get_client(self.login)
        r.ipaddr = client.ip
        r.traf = "%.2f"%float(client.traf.traf)
        r.account = "%.2f"%float(client.account - client.acctlimit)
        r.debt = "%.2f"%float(abs(client.acctlimit))
       
        t = Time()
        traf, debit = db.get_debit(client.id, t.current_day())
        r.traf_today = "%.2f"%traf
        
        traf, debit = db.get_debit(client.id, t.curent_month())
        r.traf_month = "%.2f"%traf
        
        if client.traf.limit == '0':
            r.traflimit = 'No'
        else:
            r.traflimit = client.traf.limit
        
        if client.traf.traf > client.traf.limit:
            r.traf_color = "#FF0000"
        else:
            r.traf_color = "#FFFFFF"
        
        r.model = client.rate.get_name(self.text)
      
        r.messages = self.show_messages( db.get_message(self.login) )
        
        f = file("stat.html")
        html = f.read()
        return html
    

    def process(self):
        if self.form.has_key("set_traflimit") and self.form.has_key("traflimit"):
            traflimit = self.form.getvalue("traflimit")
            try:
                traflimit = int(traflimit)
            except:
                traflimit = 0
            self.db.set_traflimit(self.login, traflimit)
        return self.show()
    

Form().run()

