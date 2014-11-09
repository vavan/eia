#!/usr/bin/python

import sys, os
import datetime
import logging
from web_base import BaseAdminForm


class AdminClients(BaseAdminForm):
        
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
    
    def show_clients_table(self):
        clients = self.db.get_clients()
        clients.sort(key = lambda x : int(x.id))
        
        self.odd(0)
        body = ''

        for c in clients:
            traf = float(c.traf.traf)
            traflimit = int(c.traf.limit)
            
            if c.traf.limit != 0 and c.traf.traf > c.traf.limit:
                status = self.text.STATUS_BLOCKED_BY_LIMIT
                status_color = 'class="red"'
            elif c.account <= c.acctlimit:
                status = self.text.STATUS_BLOCKED_BY_MONEY
                status_color = 'class="red"'
            else:
                status = self.text.STATUS_ENABLE
                status_color = ''
            
            body += '<tr %s>'%self.odd()
            body += '<td class="first"><a href="web_admin_clients.py?$session_link&client=%s">%s</a></td>'%(c.id, c.id)
            body += '<td>%s</td>'%c.name
            body += '<td>%.2f</td>'%(c.account - c.acctlimit)
            body += '<td>%s</td>'%c.rate.get_full_name(self.text)
            body += '<td %s>%s</td>'%(status_color, status)
            body += '</tr>\n'
        
        return body
    
    def show_addresses_table(self):
        addresses = self.db.get_addresses_web()
        self.odd(0)
        body = ''
        for addrid, ip, mac, uid, name in addresses:
            if ip != '' and mac != '':
                body += '<tr %s>'%self.odd()
                body += '<td class="first">%s</td>'%uid
                body += '<td>%s</td>'%name
                body += '<td>%s</td>'%ip
                body += '<td>%s</td>'%mac
                body += '</tr>\n'
        return body        
        
    def is_uniq_ip(self, theaddrid, theip, addresses, redirect_to):
        for addrid, ip, mac, uid, name in addresses:
            if theip == ip and int(theaddrid) != int(addrid):
                msg = '$DUPLICATE_IP: %s'%ip
                self.on_fail(msg, redirect_to)
                sys.exit(0)
    
    def is_uniq_mac(self, theaddrid, themac, addresses, redirect_to):
        for addrid, ip, mac, uid, name in addresses:
            if themac == mac and int(theaddrid) != int(addrid):
                msg = '$DUPLICATE_MAC: %s'%mac
                self.on_fail(msg, redirect_to)
                sys.exit(0)

    def update_addresses(self, uid):
        addresses = self.db.get_addresses_web()
        redirect_to = 'web_admin_clients.py?$session_link&client=%s'%uid
        for i in self.f:
            if i.startswith('ip_'):
                addrid = int( i[len('ip_'):] )
                ip = self.f.getvalue(i)
                self.validate_ip(ip, redirect_to)
                self.is_uniq_ip(addrid, ip, addresses, redirect_to)
                self.db.modify_address(addrid, ip = ip)
            elif i.startswith('mac_'):
                addrid = int( i[len('mac_'):] )
                mac = self.f.getvalue(i)
                mac = mac.replace('-', ':').upper()
                self.validate_mac(mac, redirect_to)
                self.is_uniq_mac(addrid, mac, addresses, redirect_to)
                self.db.modify_address(addrid, mac = mac)

    def delete_address(self, uid):
        for i in self.f:
            if i.startswith('del_'):
                addrid = int( i[len('del_'):] )
                self.db.delete_address(addrid)
    
    def show_ip_map_pairs(self, addresses):
        out = ''
        for addrid, ip, mac  in addresses:
            addrid = int(addrid)
            out += '<p><label class="left">IP:</label>'
            out += '<input class="field" type=text value="%s" name=ip_%02d>'%(ip, addrid)
            out += '<input class="drop" type=submit value="X" name=del_%02d></p>\n'%(addrid)

            out += '<p><label class="left">MAC:</label>'
            out += '<input class="field" type=text value="%s" class="field" name=mac_%02d></p>\n'%(mac, addrid)
        return out    
        
    def show_client(self, uid):
        client = self.db.get_client(uid)
        addresses = self.db.get_client_addresses(uid)
        self.r.client = uid
        self.r.name = client.name
        self.r.rate_options = self.show_rate_options(client.rate.id)
        self.r.ip_map_pairs_list = self.show_ip_map_pairs(addresses)
    
    def modify_client(self, uid):
        name = self.getvalue('name')
        passwd = self.getvalue('password')
        rate = self.getvalue('rate', int)
        self.db.modify_client(uid, name, passwd, rate)
        self.update_addresses(uid)

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
            self.db.delete_client_addresses(uid)
            uid = None
        elif 'add' in self.f:
            uid = self.add_client()
        elif 'add_addr' in self.f:
            self.db.add_client_addresses(uid)
        else:
            self.delete_address(uid)
        
        if uid:
            self.show_client(uid)
            f = file("template/admin_clients_edit.html")
        else:            
            f = file("template/admin_clients.html")
        self.r.clients_table = self.show_clients_table()
        self.r.addresses_table = self.show_addresses_table()
    
        html = f.read()
        return html


AdminClients().run()