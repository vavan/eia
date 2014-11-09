 #!/usr/bin/python

import os, sys, logging
from optparse import OptionParser
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config
import sql_db
from main import MoneyAdds
from text import TextProcessor

#sys.argv = 'a -a client -u 22 -n NAME22 -p PWD -i 192.168.0.21 -m 00-01-00:00:00:00'.split()
#sys.argv = 'a -a provider -u 112 -n NAME4 -i 192.168.0.21 -f eth2'.split()
#sys.argv = 'a -a money'.split()
#sys.argv = 'a -a money -n NAME -z +10'.split()


ADMIN = '776' # ID of CLI admin access

class Manage:
    def __init__(self):
        config.init_log()       
        if os.name == 'nt':
            self.db = sql_db.DataBase('../test/test_database.lite', True, sql = sql_db.SqlTest)
        else:
            self.db = sql_db.DataBase(config.sql_credentials, True)

    def get_uid(self, options):
        try:
            uid = int(options.uid)
        except:
            uid = None
        return uid
        
    def add_money(self, options):
        uid = self.get_uid(options)
        if uid == None and options.name:
            clients = self.db.get_clients()
            uid = self.get_client(clients, options.name)
        if uid:
            adds = MoneyAdds(options.maney)
            acct, limit = adds.apply()
            self.db.add_money(uid, acct, limit)
            self.db.update_credits(uid, adds.get_value(), adds.get_type(), ADMIN)
            print "Account of uid %s was updated by %0.2f [%s]"%\
                (uid, adds.get_value(), adds.get_type_name(self.text))
        else:
            print "Error. Can not find Client bu UID/name: '%s'/'%s'"%(options.uid, options.name)

    def buid_address_map(self):
        addresses = self.db.get_addresses()
        addr_map = {}
        for addr in addresses:
            if addr.uid not in addr_map:
                addr_map[addr.uid] = ''
            addr_map[addr.uid] += '%s,'%addr.ip
        return addr_map
    
    
    def show_clients(self):
        print "-"*79
        print " ID. %10s [      IPs       ]: acct / limit"%'Name'
        print "-"*79
        clients = self.db.get_clients()
        addresses = self.buid_address_map()
        clients.sort( key = lambda x : int(x.id) )
        for i in clients:
            print " %2s. %10s [%s]: %4.2f / %4.2f"%(i.id, i.name, addresses[i.id], i.account, i.acctlimit)
        print "-"*79
            
            
    def main(self):
        parser = OptionParser()
        parser.add_option("-u", dest="uid", type="int",\
                          help="Client UID")
        parser.add_option("-n", dest="name", \
                          help="Client name")
        parser.add_option("-m", dest="maney",\
                          help="Maney to add for client specified by -n/u")
        (options, args) = parser.parse_args()
        
        text_base_path = os.path.join(os.path.dirname(sys.argv[0]), '../web/')
        self.text = TextProcessor(text_base_path).get_language(TextProcessor.ENGLISH)
        if (options.uid or options.name) and options.maney:
            self.add_maney(options)
        else:
            self.show_clients()
            


Manage().main()

