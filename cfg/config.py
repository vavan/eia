'''
    Configuration file
'''

import logging, os

sql_credentials = { "host": "127.0.0.1", "user": "easy", "pwd": "zhopa", "database": "easy" }

lan = 'eth3'

web_user = 'easy'
web_address = '10.0.0.37'
web_port = 80

language = 1

period = 19

dhcp_config = '/var/lib/dhcp/etc/dhcp_clients.conf'

log_file = '/var/log/easy.log'

def init_log():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=log_file,
                        filemode='a'
                        )


if os.name == 'nt':
    #for emulation/test only
    dhcp_config = 'dhcp_clients.conf'
    log_file = 'c:/easybs.log'
    web_address = ''
    language = 0


