#!/usr/bin/python

import os, sys, re
from collections import defaultdict
import traceback, StringIO, logging
import datetime

sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config
from sql_db import DataBase
from point import PointBuilder, ClientPoint, ProviderPoint, PointList
from dhcp import Dhcp
    

class AAA:
    MEG = 1000.0*1000.0
    
    def __init__(self, rate_mode):
        logging.info( "Start AAA %s"%rate_mode)
        self.rate_mode = rate_mode
        self.db = DataBase(config.sql_credentials)
    
    def get_clients(self):
        clients = self.db.get_clients()
        addresses = self.db.get_addresses()
        address_map = defaultdict(list)
        for i in addresses:
            address_map[i.uid].append(i)
        
        for c in clients:
            if c.id in address_map:
                c.addresses = address_map[c.id]
        return clients
    
    def get_providers(self):
        return self.db.get_providers()

    def is_allowed(self, client):
        if client.account > client.acctlimit:
            if client.traf.limit != 0:
                if client.traf.traf < client.traf.limit:
                    return True
            else:
                return True

    def get_allowed(self, clients, providers):
        allowed_points = PointList()
        for p in providers:
            allowed_points.append( ProviderPoint(p.iface) )
        for c in clients:
            if self.is_allowed(c):
                for a in c.addresses:
                    client_point = ClientPoint(a.ip)
                    client_point.set_mac(a.mac)
                    client_point.set_channel(c.rate.channel)
                    allowed_points.append( client_point )
        return allowed_points
    
    def auth(self, allowed_points, existed_points):
        for allowed in allowed_points:
            if allowed in existed_points:
                i = existed_points.index(allowed)
                if not existed_points[i].equal(allowed):
                    logging.debug("Apoint: %s; Epoint: %s"%(str(allowed), str(existed_points[i])))
                    existed_points.erase(allowed)
                    allowed.add()
            else:
                allowed.add()
        for existed in existed_points:
            if existed not in allowed_points:
                existed_points.erase(existed)


    def acct_client(self, client, time, bytes):
        if client.account > client.acctlimit:
            mbytes = bytes / self.MEG
            debit = client.rate.apply(mbytes, self.rate_mode)
            if mbytes != 0 or debit != 0:
                self.db.update_debits(client.id, mbytes, debit, client.rate.id, time)
                self.db.update_client_account(client.id, mbytes, debit)
                logging.debug( "Acct client: %s %s %s"%(client.id, mbytes, debit))
            
    def acct_provider(self, provider, time, bytes):
        mbytes = bytes / self.MEG
        debit = provider.rate.apply(mbytes, self.rate_mode)
        if mbytes != 0 or debit != 0:
            self.db.update_debits(provider.id, mbytes, debit, provider.rate.id, time)
            logging.debug( "Acct provider: %s %s %s"%(provider.id, mbytes, debit))

    def acct(self, existed_points, clients, providers):
        time = datetime.datetime.now()
        existed_map = dict(map(lambda x: (x.get_key(x), x), existed_points))
        for c in clients:
            for a in c.addresses:
                if a.ip in existed_map:
                    self.acct_client(c, time, existed_map[a.ip].bytes)
                else:
                    self.acct_client(c, time, 0)
        for p in providers:
            if p.iface in existed_map:
                self.acct_provider(p, time, existed_map[p.iface].bytes)


    def dhcp(self, clients):
        allowed_pairs = []
        for c in clients:
            for a in c.addresses:
                allowed_pairs.append( (a.mac, a.ip) )
        dhcp = Dhcp(config.dhcp_config)
        existed_pairs = dhcp.parse()
        if existed_pairs != allowed_pairs:
            dhcp.serialize(allowed_pairs)
            dhcp.restart()
            return True

    def main(self):
        existed_points = PointBuilder().build()
        providers = self.get_providers()
        clients = self.get_clients()
        allowed_points = self.get_allowed(clients, providers)
        
        self.acct(existed_points, clients, providers)
        self.auth(allowed_points, existed_points)
        self.dhcp(clients)



def log_except(exc):
    stream = StringIO.StringIO()
    traceback.print_exception(getattr(exc,"__class__"), exc, sys.exc_traceback, None, stream)
    logging.error(stream.getvalue())

if __name__ == '__main__':
    config.init_log()       
    try:
        if len(sys.argv) > 1:
            rate_mode = sys.argv[1]
        else:
            rate_mode = None
        AAA(rate_mode).main()
    except Exception, e:
        logging.error( 'Unhandled exception in AAA:' )
        log_except( e )
