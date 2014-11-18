#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time

class Form(BaseClientForm):

    def add_alive(self):
        user = self.getvalue('user')
        device = self.getvalue('device')
        duration = self.getvalue('duration', int)
        alive = self.db.check_alive(user)
        if alive:
            device, time, duration = alive
            logging.debug("Alive: %s %s %s"%(device, time, duration))
        else:
            self.db.start_alive(user, device, duration*60)

    def show_users(self):
        body = ''
        clients = self.db.get_clients()
        length = len(clients)
        for c in clients:
            body += '<input type="radio" name="user" value="%s" id="u%s" class="register-switch-input">'%(c.id, c.name)
            body += '<label style="width:%0.2d%%;" for="u%s" class="register-switch-label">%s:%d</label>'%(100/length, c.name, c.name, c.account)
        return body
        
    def show_devices(self):
        body = ''
        devices = self.db.get_devices()
        length = len(devices)
        for d in devices:
            body += '<input type="radio" name="device" value="%s" id="d%s" class="register-switch-input">'%(d.id, d.name)
            body += '<label style="width:%0.2d%%;" for="d%s" class="register-switch-label">%s</label>'%(100/length, d.name, d.name)
        return body
        
    def show(self):
        if 'start' in self.f:
            self.add_alive()

        self.r.users = self.show_users()
        self.r.devices = self.show_devices()
             
        f = file("template/client_main.html")
        html = f.read()
        return html
    

    def process(self):
        return self.show()
    

Form().run()

