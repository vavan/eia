#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from main import Device
from web_base import BaseAdminForm


class AdminRates(BaseAdminForm):
          
          
    def do_add(self):
        name = self.getvalue('name')
        mac = self.getvalue('mac')
        redirect_to = 'web_admin_devices.py?$session_link'
        self.validate_mac(mac, redirect_to)
        self.db.add_device(name, mac)
    
    def do_delete(self, recordid):
        self.db.delete_device(recordid)
    
    def show(self):
        out = ''
        devices = self.db.get_devices()
        self.odd(0)
        for d in devices:
            out += '<tr %s>'%self.odd()
            out += '<td class="first"><a href="web_admin_devices.py?$session_link&delete=%s">Delete</a></td>'%d.id
            out += '<td>%s</td>'%d.name
            out += '<td>%s</td>'%d.mac
            out += '</tr>\n'
        return out
    
    def process(self):
        if 'add' in self.f:
            self.do_add()
        elif 'delete' in self.f:
            record_id = self.getvalue("delete", int)
            self.do_delete(record_id)
    

        self.r.devices = self.show()
        
        f = file("template/admin_devices.html")
        html = f.read()
        return html

AdminRates().run()