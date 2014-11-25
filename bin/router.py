import sys, os, re
import urllib, urllib2
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config



"""
<a href="connected_devices_computers_edit.php?&computer_name=android-beb7846b1eba950&staticIPAddress=10.0.0.27&ip_type=DHCP&connection=1&computer_mac=C8:AA:21:31:1D:12
&comments=&index=-1" class="btn">Edit</a>
"""

class Router:
    row_re = re.compile('<th class="row-label alt">\d+</th>\s*<td>.*?</td>\s*<td>(.*?)</td>\s*<td>.*?</td>\s*<td.*?</td>\s*<td(.*?)</td>\s*')
    id_re = re.compile('<a href="managed_devices\.php\?&delete=(\d+)&del_type=0"')
    map_re = re.compile('connected_devices_computers_edit\.php\?&computer_name=.*?'
        '&staticIPAddress=(.*?)&ip_type=DHCP&connection=\d+&computer_mac=((?:[A-F0-9]{2}:){5}[A-F0-9]{2})\s*&comments=&index=')
    
    def __init__(self):
        for k, v in config.router.iteritems():
            setattr(self, k, v)
        self.logedin = False
            
    def login(self):
        if not self.logedin:
            url = 'http://%s/home_loggedout.php'%self.addr
            values = {'username' : self.username,
                      'password' : self.password}
            req = urllib2.Request(url, urllib.urlencode(values))
            response = urllib2.urlopen(req)
            self.logedin = True

    def add(self, mac):
        self.login()
        name = mac.replace(':', '')
        url = 'http://%s/managed_devices_add_computer_blocked.php'%self.addr
        values = {'computer' : 'custom', 'custom_name' : name, 'custom_mac' : mac, 'block': 'yes' }
        values = urllib.urlencode(values)
        req = urllib2.Request(url, values)
        logging.debug("Add blocked device to router")
        response = urllib2.urlopen(req)

    def __find(self, mac):
        url = 'http://%s/managed_devices.php'%self.addr
        response = urllib2.urlopen(url)
        device_page = response.read()
        for _mac, _href in Router.row_re.findall(device_page):
            if _mac == mac:
                return Router.id_re.search(_href).group(1)
    
    def remove(self, mac):
        self.login()
        device = self.__find(mac)
        name = mac.replace(':', '')
        url = 'http://%s/managed_devices.php?&delete=%s&del_type=0'%(self.addr, device)
        logging.debug("Remove blocked device from router")
        response = urllib2.urlopen(url)

    def address_map(self):
        url = 'http://%s/connected_devices_computers.php'%self.addr
        response = urllib2.urlopen(url)
        map_page = response.read()
        return Router.map_re.findall(map_page)
            

        