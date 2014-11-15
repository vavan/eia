'''
    Configuration file
'''

import logging, os, sys

sql = { "database": "easy.sql" }

lan = 'eth3'

web_user = 'easy'
web_address = '0.0.0.0'
web_port = 80

language = 0

log_file = '/var/log/easy.log'
if os.name == 'nt':
    log_file = 'C:/Users/vova/Projects/kids/eia/easy.log'

def init_log():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=log_file,
                        filemode='a')




