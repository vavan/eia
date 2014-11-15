#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseAdminForm, Calendar
from main import MoneyAdds

    
class Totals:
    def __init__(self):
        self.traf = 0
        self.money = 0
        self.balance = 0
        self.debt = 0

class AdminAdd(BaseAdminForm):
    
    def prepare_client(self, client):
        if client.id in self.stat:
            client_traf = self.stat[client.id]
            traf = client_traf[0]
        else:
            traf = 0
        self.total.traf += traf
        
        if client.id in self.credits:
            money = float(self.credits[client.id])
            if money > 0:
                self.total.money += money
        else:
            money = 0
        
        account = client.account
        if account >= 0:
            self.total.balance += account

        self.total.debt += abs(client.acctlimit)
        return (traf, money)
    
    def show_adds_list(self, time_range, selected):
        clients = self.db.get_clients()
        clients.sort(key = lambda x : int(x.id))
        
        self.stat = self.db.get_debits(time_range)
        credits = self.db.get_credits(time_range)
        if credits:
            self.credits = dict( credits )
        else:
            self.credits = {}
        self.total = Totals()
        
        self.odd(0)
        body = ''
        for c in clients:
               
            body += '<tr %s>'%self.odd()
            body += '<td class="first">%s</td>'%(c.name)
            
            traf, money = self.prepare_client(c)
            account = c.account - c.acctlimit
            body += '<td>%.2f</td><td>%.2f</td>'%(traf, money)
            
            if str(selected) == str(c.id):
                mark = ' class="selected"'
            else:
                mark = ''
                
            body += "<td%s>%.2f</td>"%(mark, account)
            body += '<td>%.2f</td>'%(abs(c.acctlimit))
            
            body += "<td align=right>"
            body += '<input name=moneyadd_%s value="" size=4>'%c.id
            body += '<input type="submit" name=add_%s value="+">'%c.id
            body += "</td></tr>\n"
            
        body += '<tr class="bottom">'
        body += '<td class="first">TOTAL</td>'
        body += '<td>%.2f</td>'%self.total.traf
        body += '<td>%.2f</td>'%self.total.money
        body += '<td>%.2f</td>'%self.total.balance
        body += '<td>%.2f</td>'%self.total.debt
        body += '<td>&nbsp;</td></tr>\n'
        return body
   
    def show_credits(self, time_range):
        body = ''
        total = 0
        credits = self.db.get_credits_history(time_range)
        self.odd(0)
        if credits: 
            for credit in credits:
            
                client = credit[0]
                money = float(credit[1])
                when = credit[2]
                paytype = MoneyAdds.type_name(int(credit[3]), self.text)
                
                if money > 0:
                    total += money
                body += '<tr %s>'%self.odd()
                body += '<td class="first">%s</td><td>%s</td><td>%.2f</td><td>%s</td></tr>\n'%( when, client, money, paytype )
            
        body += '<tr class="bottom">'
        body += '<td class="first">TOTAL</td><td></td><td>%.2f</td><td></td></tr>\n'%(total)
        return body, total
        
    def get_providers_list(self):
        providers = self.db.get_providers()
        provs = []
        for i in providers:
            provs.append(i.id)
        return provs        
        
    def show_summary_table(self, time_range, income):
        out = ''
        sum_mbytes = 0
        sum_money = 0
        providers = self.db.get_providers()
        self.odd(0)
        for p in providers:
            mbytes, money = self.db.get_debit( p.id, time_range )
            sum_mbytes += mbytes
            sum_money += money
            out += '<tr %s>'%self.odd()
            out += '<td class="first">%s</td><td>%.2f</td><td>%.2f</td><td>-</td></tr>\n'%( p.name, mbytes, money )
        
        sum_profit = income - sum_money
        out += '<tr class="bottom">'
        out += '<td class="first">TOTAL</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>\n'%(sum_mbytes, sum_money, sum_profit)
        return out        
    
    def show(self, selected):
        c = Calendar(self.f)
        time_range = c.get_time_range()

        self.r.select_month = c.select_month()
        self.r.adds_list = self.show_adds_list(time_range, selected)
        self.r.credit_history, income = self.show_credits(time_range)
        self.r.summary_table = self.show_summary_table(time_range, income)
              
        f = file("template/admin_add.html")
        html = f.read()
        return html
    
    def parse_adds(self):
        uid = 0
        adds = None
        for i in self.f:
            if i.startswith('add_'):
                uid = i[4:]
                if self.f.has_key('moneyadd_'+uid):
                    adds = self.f.getvalue('moneyadd_'+uid)
                    adds = MoneyAdds(adds)
        return uid, adds
    
    def process(self):
        uid, adds = self.parse_adds()
        if uid > 0 and adds != None and adds.get_value() != 0:
            selected = uid
            acct, limit = adds.apply()
            self.db.add_money(uid, acct, limit)
            self.db.update_credits(uid, adds.get_value(), adds.get_type(), self.login)
        else:
            selected = 0
           
        return self.show(selected)

 
    
AdminAdd().run()
