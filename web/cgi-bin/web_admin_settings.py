#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseAdminForm


class AdminSettings(BaseAdminForm):
        
    def process(self):
        if 'ok' in self.f:
            name = self.getvalue("name")
            passwd = self.getvalue("passwd")
            self.db.update_admin(name, passwd, self.login)
       
        self.r.name = self.db.get_admin(self.login)[0]
        
        f = file("template/admin_settings.html")
        html = f.read()
        return html

AdminSettings().run()