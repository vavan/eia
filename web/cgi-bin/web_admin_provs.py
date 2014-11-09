#!/usr/bin/python

import sys, os
import datetime
import logging
from web_base import BaseAdminForm, Calendar


class AdminProvs(BaseAdminForm):

        
    def show_rate_options(self, rate_id):
        out = ''
        rates = self.db.get_rates()
        for rate in rates:
            if rate_id == rate.id:
                selected = 'selected'
            else:
                selected = ''
            out += '<option value="%s" %s>%s</option>\n'%(rate.id, selected, rate.get_full_name(self.text))
        return out

    def show_providers_table(self, providers, time_range):
        providers.sort(key = lambda x : int(x.id))
        
        self.odd(0)
        body = ''
        for p in providers:
            mbytes, sum = self.db.get_debit( p.id, time_range )
            
            body += '<tr %s>'%self.odd()
            body += '<td class="first"><a href="web_admin_provs.py?$session_link&prov=%s">%s</a></td>'%(p.id, p.id)
            body += '<td>%s</td>'%p.name
            body += '<td>%s</td>'%p.ip
            body += '<td>%s</td>'%p.iface
            body += '<td>%s</td>'%p.rate.get_name(self.text)
            body += '</tr>\n'
        return body
    
    def is_uniq_iface(self, theiface, theid, redirect_to):
        providers = self.db.get_providers()
        for p in providers:
            if theiface == p.iface and int(theid) != int(p.id):
                msg = '$DUPLICATE_IFACE: %s'%theiface
                self.on_fail(msg, redirect_to)
                sys.exit(0)
    
                
    def modify_provider(self, uid):
        name = self.getvalue('name')
        rate = self.getvalue('rate', int)
        ip = self.getvalue('ip')
        redirect_to = 'web_admin_provs.py?$session_link&prov=%s'%uid
        iface = self.getvalue('iface')
        self.validate_ip(ip, redirect_to)
        self.is_uniq_iface(iface, uid, redirect_to)
        self.db.modify_provider(uid, name, ip, iface, rate)
        
    def show_provider(self, uid):
        provider = self.db.get_provider(uid)
        self.r.prov = uid
        self.r.name = provider.name
        self.r.ip = provider.ip
        self.r.iface = provider.iface
        self.r.rate_options = self.show_rate_options(provider.rate.id)
    
    
    def process(self):
        if 'prov' in self.f:
            uid = self.getvalue("prov", int)
        else:
            uid = None
            
        if 'ok' in self.f:
            self.modify_provider( uid )
            uid = None
        elif 'delete' in self.f:
            self.db.del_provider( uid )
            uid = None
        elif 'add' in self.f:
            uid = self.db.add_provider()

        if uid:
            self.show_provider(uid)
            f = file("template/admin_provs_edit.html")
        else:            
            f = file("template/admin_provs.html")
        

        c = Calendar(self.f)
        time_range = c.get_time_range()
        providers = self.db.get_providers()
              
        self.r.select_month = c.select_month()
        self.r.providers_table  = self.show_providers_table(providers, time_range)
        html = f.read()
        return html


AdminProvs().run()