#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time
from main import MoneyAdds

class Form(BaseClientForm):
    
    def show_credits(self):
        body = ''
        total = 0
        credits = self.db.get_client_credits_history(self.login)
        self.odd(0)
        for credit in credits:
            money = float(credit[0])
            when = credit[1]
            paytype = MoneyAdds.type_name(int(credit[2]), self.text)
            
            if money > 0:
                total += money
            body += '<tr %s>'%self.odd()
            body += '<td class="first">%s</td><td>%.2f</td><td>%s</td></tr>\n'%( when, money, paytype )
            
            
        body += '<tr class="bottom">'
        body += '<td class="first">TOTAL</td><td>%.2f</td><td></td></tr>\n'%(total)
        return body
        
        
    def process(self):
        self.r.credit_list = self.show_credits()
    
        f = file("template/client_credit.html")
        html = f.read()
        return html
    

Form().run()

