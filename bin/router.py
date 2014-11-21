import sys, os, re
import urllib, urllib2
import logging
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config



class Router:
    row_re = re.compile('<th class="row-label alt">\d+</th>\s*<td>.*?</td>\s*<td>(.*?)</td>\s*<td>.*?</td>\s*<td.*?</td>\s*<td(.*?)</td>\s*')
    id_re = re.compile('<a href="managed_devices\.php\?&delete=(\d+)&del_type=0"')

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

