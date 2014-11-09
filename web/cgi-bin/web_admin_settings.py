#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from main import Rate
from web_base import BaseAdminForm


class AdminSettings(BaseAdminForm):
        
    def process(self):
        if 'ok' in self.f:
            name = self.getvalue("name")
            passwd = self.getvalue("passwd")
            ip = self.getvalue("ip")
            redirect_to = 'web_admin_settings.py?$session_link'
            self.validate_ip(ip, redirect_to)
            self.db.update_admin(name, passwd, ip, self.login)
       
        self.r.name, self.r.ip = self.db.get_admin(self.login)
        
        f = file("template/admin_settings.html")
        html = f.read()
        return html

AdminSettings().run()