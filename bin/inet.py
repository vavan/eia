#!/usr/bin/python
import os, re, sys, logging, time
import urllib


LIST_OF_IPS = (
        '195.214.195.105', #ukr.net
        '74.125.45.100',   #google.com
        '195.5.5.185',     #default gw
        '69.17.117.207',   #speedtest.net
        )


LIST_OF_NAMES = (
        'ukr.net',
        'ya.ru',  
        'google.com',
        )

   
def ping(route):
    cmd = 'ping -q -c5 -W2 %s'%route
#    print cmd
    data = os.popen(cmd)
    data = data.read()
    lost_persent = re.search(', (\d+)% packet loss,', data)
    if data:
        lost_persent = int(lost_persent.group(1))
        is_up = lost_persent < 10
        if is_up:
            avg_delay = re.search('rtt min/avg/max/mdev = [0-9.]+/([0-9.]+)/[0-9.]+/[0-9.]+ ms', data)
            if avg_delay:
                avg_delay = avg_delay.group(1)
        else:
            avg_delay = None
        return is_up, avg_delay


class Opener(urllib.FancyURLopener):
   def prompt_user_passwd(self, host, realm):
       return ('admin','vjcngfnjyf')

            
def reboot_dsl():           
    u = Opener().open('http://192.168.1.1/rebootinfo.cgi')
    feedback = u.read()
    logging.info('DSL has been rebooted: %s'%feedback[708:])


def test_servers(server_list):
    total_down = True
    for i in server_list:
        is_up, delay = ping(i)
        if is_up:
            logging.info('Ping %s, delay:%s'%(i, delay) )
        else:
            logging.info('\tDown %s'%(i) )
        if is_up:
            total_down = False
    return total_down

            
def main():
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    filename='/var/log/inet.log',
                    filemode='a')


    ip_down = test_servers(LIST_OF_IPS)
    if ip_down == True:
        logging.info('IP is down: restart dsl')
        reboot_dsl()
        return
    

    name_down = False
    #test_servers(LIST_OF_NAMES)
    if name_down:
        logging.info('Restart named')
        os.system('service named restart')
        time.sleep(2)
        name_down = test_servers(LIST_OF_NAMES)
        if name_down:
            logging.info('DNS is down: restart dsl')
            reboot_dsl()
    
    


if len(sys.argv) == 2:
    logging.info( "Reboot DSL" )
    reboot_dsl()
else:   
    main()