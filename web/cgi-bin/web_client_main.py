#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time
from rate import Rate

class Form(BaseClientForm):

    def on_alredy_alive(self, user, device, duration_left):
        device = self.db.get_device(device)
        self.alert("You have started on %s already. %s min left"%(device.name, duration_left/60), 
            '/cgi-bin/web_client_main.py', '#00FF00')

    def on_new_alive(self, user, device):
        duration = self.getvalue('duration', int)
        t = Time()
        today_used, debit = self.db.get_debit(user.id, t.current_day())
        cost = Rate().apply(today_used, duration)
        if user.account >= cost:
            self.db.start_alive(user.id, device.id, duration*60)
            self.db.update_debits(user.id, duration, cost, 0, datetime.datetime.now())
            self.db.update_client_account(user.id, cost)
            self.alert("%s starts playing on %s. Paid %d$CR"%(user.name, device.name, cost), '/cgi-bin/web_client_main.py', '#00FF00')
        else:
            self.alert("Your balance is too low", '/cgi-bin/web_client_main.py', '#FF0000')
    
    def add_alive(self):
        user = self.db.get_client(self.getvalue('user'))
        device = self.db.get_device(self.getvalue('device'))

        self.db.expire_alive()
        alive = self.db.get_alive_by_user(user.id)
        if alive:
            other_device, duration_left = alive[0]
            self.on_alredy_alive(user, other_device, duration_left)
        else:
            other_user = self.db.get_alive_by_device(device.id)
            if other_user:
                self.alert("%s is used by %s"%(device.name, other_user[0][0]), '/cgi-bin/web_client_main.py', '#FF0000')
            else:
                self.on_new_alive(user, device) 
                
    def show_users(self):
        body = ''
        clients = self.db.get_clients()
        length = len(clients)
        for c in clients:
            body += '<input type="radio" name="user" value="%s" id="u%s" class="register-switch-input">'%(c.id, c.name)
            body += '<label style="width:%0.2d%%;" for="u%s" class="register-switch-label">%s:&nbsp%d$CR</label>'%(100/length, c.name, c.name, c.account)
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

