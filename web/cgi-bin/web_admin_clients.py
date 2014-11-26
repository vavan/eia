#!/usr/bin/python

import sys, os
import datetime
import logging
from web_base import BaseAdminForm


class AdminClients(BaseAdminForm):

    def __init__(self):
        BaseAdminForm.__init__(self)

   
    def show_clients_table(self):
        clients = self.db.get_clients()
        clients.sort(key = lambda x : int(x.id))
        
        self.odd(0)
        body = ''

        for c in clients:
            
            if c.account <= 0:
                status = self.text.STATUS_BLOCKED_BY_MONEY
                status_color = 'class="red"'
            else:
                status = self.text.STATUS_ENABLE
                status_color = ''
            
            body += '<tr %s>'%self.odd()
            body += '<td class="first"><a href="web_admin_clients.py?$session_link&client=%s">%s</a></td>'%(c.id, c.id)
            body += '<td>%s</td>'%c.name
            body += '<td>%.2f</td>'%(c.account)
            body += '<td %s>%s</td>'%(status_color, status)
            body += '</tr>\n'
        
        return body       
      
    def show_client(self, uid):
        client = self.db.get_client(uid)
        self.r.client = uid
        self.r.name = client.name
        if client.super:
            self.r.super_yes = 'checked'
            self.r.super_no = ''
        else:
            self.r.super_yes = ''
            self.r.super_no = 'checked'
        
    
    def modify_client(self, uid):
        name = self.getvalue('name')
        super = self.getvalue('super')
        super = super == 'yes'
        self.db.modify_client(uid, name, super)

    def add_client(self):
        return self.db.add_client()
   
    def process(self):
        if 'client' in self.f:
            uid = self.f.getvalue("client")
        else:
            uid = None
    
        if 'ok' in self.f:
            self.modify_client(uid)
            uid = None
        elif 'delete' in self.f:
            self.db.delete_client(uid)
            uid = None
        elif 'add' in self.f:
            uid = self.add_client()
        
        if uid:
            self.show_client(uid)
            f = file("template/admin_clients_edit.html")
        else:            
            f = file("template/admin_clients.html")
        self.r.clients_table = self.show_clients_table()
    
        html = f.read()
        return html


AdminClients().run()