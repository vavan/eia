#!/usr/bin/python

import sys, os
import datetime
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from web_base import BaseClientForm
from request import Time
from rate import Rate
from router_hal import RouterHal

class Form(BaseClientForm):
    SUPER_DURATION = 15

    def on_alredy_alive(self, user, device, duration_left):
        device = self.db.get_device(device)
        self.alert("You have started on %s already. %s min left"%(device.name, duration_left/60), 
            '/cgi-bin/web_client_main.py', '#00FF00')

    def on_new_alive(self, user, device):
        duration = self.getvalue('duration', int)
        t = Time()
        today_used, debit = self.db.get_debit(user.id, t.current_day())
        cost = Rate().apply(today_used, duration)
        if cost == None:
            self.alert("You've used all available time for today", '/cgi-bin/web_client_main.py', '#FF0000')
        elif user.account < cost:
            self.alert("Your balance is too low", '/cgi-bin/web_client_main.py', '#FF0000')
        else:
            self.db.start_alive(user.id, device.id, duration*60)
            self.db.update_debits(user.id, duration, cost, 0, datetime.datetime.now())
            self.db.update_client_account(user.id, cost)
            self.alert("%s starts playing on %s. Paid %d$CR"%(user.name, device.name, cost), '/cgi-bin/web_client_main.py', '#00FF00')
            RouterHal(self.db).allow(device.id)
    
    def add_alive(self, user, device):
        self.db.expire_alive()
        alive = self.db.get_alive_by_user(user.id)
        if alive:
            other_device, duration_left = alive[0]
            self.on_alredy_alive(user, other_device, duration_left)
        else:
            if user.super:
                self.db.cancel_alive(device.id)
                self.db.start_alive(user.id, device.id, Form.SUPER_DURATION*60)
                RouterHal(self.db).allow(device.id)
            else:
                other_user = self.db.get_alive_by_device(device.id)
                if other_user:
                    self.alert("%s is used by %s"%(device.name, other_user[0][0]), '/cgi-bin/web_client_main.py', '#FF0000')
                else:
                    self.on_new_alive(user, device) 
                
    def show_users(self):
        body = ''
        clients = self.db.get_clients()
        length = len(filter(lambda x: not x.super ,clients))
        for c in clients:
            if not c.super:
                body += '<input type="radio" name="user" value="%s" id="u%s" class="register-switch-input">'%(c.id, c.name)
                body += '<label style="width:%0.2d%%;" for="u%s" class="register-switch-label">%s:&nbsp%d$CR</label>'\
                %(100/length, c.name, c.name, c.account)
        return body
        
    def show_devices(self, selected):
        body = ''
        devices = self.db.get_devices()
        length = len(devices)
        for d in devices:
            if d.id == selected:
                checked = 'checked'
            else:
                checked = ''
            body += '<input type="radio" name="device" value="%s" id="d%s" class="register-switch-input" %s>'%(d.id, d.name, checked)
            body += '<label style="width:%0.2d%%;" for="d%s" class="register-switch-label">%s</label>'%(100/length, d.name, d.name)
        return body
        
    def show(self):
        ip = os.environ["REMOTE_ADDR"]
        device = self.db.get_device_by_ip(ip)

        show = True
        if 'start' in self.f and device:
            if 'user_name' in self.f:
                user = self.db.get_client_by_name(self.getvalue('user_name'))
            else:
                user = self.db.get_client(self.getvalue('user'))
            if user.super:
                show = False
            #device = self.db.get_device(device)
            self.add_alive(user, device)

        if show:
            self.r.users = self.show_users()
            self.r.devices = self.show_devices(device)
            f = file("template/client_main.html")
            html = f.read()
        else:
            html = ''
        return html

    def process(self):
        return self.show()
    

Form().run()

