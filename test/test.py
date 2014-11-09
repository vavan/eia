#!/usr/bin/python

import sys, os
import time
import unittest
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../'))
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config;
from bin.aaa import AAA
from bin.sql_db import *
from bin.firewall import Firewall
from bin.rules import RuleId
from bin.point import PointList, ClientPoint, ProviderPoint
from test_aaa import TestAAA


class TestAcctContainer:
    def __init__(self, parent):
        self.debits = []
        self.clients = []
        parent.update_debits = self.update_debits
        parent.update_client_account = self.update_client_account

    def update_debits(self, uid, mbytes, debit, rate, time):
        self.debits.append( [uid, mbytes, debit, rate] )
    
    def update_client_account(self, uid, mbytes, debit):
        self.clients.append( [uid, mbytes, debit] )

class TestAuthContainer:
    def __init__(self):
        self.providers = []
        self.clients = []
        self.erase = []
        Firewall.add_provider = self.add_provider
        Firewall.add_client = self.add_client
        Firewall.erase = self.erase_point

    def add_provider(self, iface):
        self.providers.append(iface)

    def add_client(self, ip, mac, channel):
        self.clients.append( [ip, mac, channel] )

    def erase_point(self, rule_id):
        self.erase.append(rule_id)
        

class Main(unittest.TestCase):
    
    def create_aaa(self):
        t = TestAAA('traf_based', ':memory:')
        t.db.sql.load('ut_database.sql')
        return t
    
    def create_existed_points(self, clients, providers):
        existed_points = PointList()
        for i in clients:
            c = ClientPoint(i[0])
            c.mac = i[1]
            c.channel = i[2]
            c.bytes = i[3]
            c.set_id( i[4] )
            existed_points.append(c)
        for i in providers:
            c = ProviderPoint(i[0])
            c.bytes = i[1]
            c.set_id( i[2] )
            existed_points.append(c)
        return existed_points
    
    def create_cp(self):
        clients = [
            ['192.168.0.2', '00:04:61:A7:71:BE', 0, AAA.MEG*101, RuleId('t','c', 1002)],
            ['192.168.0.3', '00:0E:2E:BE:46:27', 0, AAA.MEG*103, RuleId('t','c', 1007)],
        ]
        providers = [ ['eth3', AAA.MEG*201, RuleId('t','c',2001)], ]
        return clients, providers
    
    def create_acct(self, t, existed_points):
        tac = TestAcctContainer(t.db)
        providers = t.get_providers()
        clients = t.get_clients()
        t.acct(existed_points, clients, providers)
        return tac.debits, tac.clients
    
    def create_gold_acct(self):
        '''[uid, mbytes, debit, rate]'''
        gold_d = [
            [ 2, 101.0, 202, 0 ],
            [ 3, 103.0, 206, 0 ],
            [ 101, 201.0, 402, 0 ],
        ]
        '''[uid, mbytes, debit]'''
        gold_c = [
            [ 2, 101.0, 202 ],
            [ 3, 103.0, 206 ],
        ]
        return gold_d, gold_c
  
    def create_auth(self, t, allowed_points, existed_points):
        tac = TestAuthContainer()
        t.auth(allowed_points, existed_points)
        return tac.clients, tac.providers, tac.erase


#ACCT  
  
    def test_acct_normal(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d, gold_c = self.create_gold_acct()
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_one_more(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        eclients.append(
            ['192.168.0.4', '00:0E:2E:BE:46:27', 0, AAA.MEG*105, RuleId('t','c',1005)],
        )
        existed_points = self.create_existed_points(eclients, eproviders)
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d, gold_c = self.create_gold_acct()
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_one_less(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        del eclients[1]
        existed_points = self.create_existed_points(eclients, eproviders)
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d, gold_c = self.create_gold_acct()
        del gold_d[1]
        del gold_c[1]
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_another_rate(self):
        t = self.create_aaa()
        t.rate_mode = 'daily'
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d, gold_c = self.create_gold_acct()
        #should account 'traf_based' even when called as 'daily'
        #for i in gold_d + gold_c:
        #    i[2] = 0
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_daily(self):
        t = self.create_aaa()
        t.rate_mode = 'daily'
        eclients, eproviders = self.create_cp()
        eclients.append(
            ['192.168.0.4', ':', 0, AAA.MEG*107, RuleId('t','c',1007)],
        )
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("insert into addresses values (4, 4, '192.168.0.4', ':')")        
        t.db.sql.update("insert into users values (4, '3rd', '1',  10, 0, 3, 0, 0, '')")
        t.db.sql.update("update providers set rate = 10")
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d = [
            [ 2, 101.0, 202.0, 0 ],
            [ 3, 103.0, 206.0, 0 ],
            [ 4, 107.0, 500.0, 3 ],
            [ 101, 201.0, 0, 10 ],
        ]
        gold_c = [
            [ 2, 101.0, 202.0 ],
            [ 3, 103.0, 206.0 ],
            [ 4, 107.0, 500.0 ],
        ]
            
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_monthly(self):
        t = self.create_aaa()
        t.rate_mode = 'monthly'
        eclients, eproviders = self.create_cp()
        eclients += [
            ['192.168.0.4', ':', 0, AAA.MEG*109, RuleId('t','c',1007)],
            ['192.168.0.5', ':', 0, AAA.MEG*111, RuleId('t','c',1009)],
        ]
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("insert into addresses values (4, 4, '192.168.0.4', ':')")
        t.db.sql.update("insert into addresses values (5, 5, '192.168.0.5', ':')")        
        t.db.sql.update("insert into users values (4, '4', '1', 10, 0, 3, 0, 0, '')")
        t.db.sql.update("insert into users values (5, '5', '1', 10, 0, 10, 0, 0, '')")
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d = [
            [ 2, 101.0, 202, 0 ],
            [ 3, 103.0, 206, 0 ],
            [ 4, 109.0, 0, 3 ],
            [ 5, 111.0, 250.0, 10 ],
            [ 101, 201.0, 402.0, 0 ],
        ]
        gold_c = [
            [ 2, 101.0, 202.0 ],
            [ 3, 103.0, 206.0 ],
            [ 4, 109.0, 0 ],
            [ 5, 111.0, 250.0 ],
        ]
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )

    def test_acct_nomoney(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        
        t.db.sql.update("update users set account = 0 where uid = '2'")
        debits, clients = self.create_acct(t, existed_points)
        gold_d, gold_c = self.create_gold_acct()
        del gold_d[0]
        del gold_c[0]
        
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )        

    def test_acct_limit_n_daily(self):
        t = self.create_aaa()
        t.rate_mode = 'daily'
        eclients, eproviders = self.create_cp()
        eclients.append(
            ['192.168.0.4', ':', 0, AAA.MEG*107, RuleId('t','c',1007)],
        )
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("insert into addresses values (4, 4, '192.168.0.4', ':')")        
        t.db.sql.update("insert into users values (4, '3rd', '1',  10, 0, 3, 0, 0, '')")
        t.db.sql.update("update users set traf = 2, traflimit = 1, rate = 3 where uid = '4'")
        t.db.sql.update("update providers set rate = 10")
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d = [
            [ 2, 101.0, 202.0, 0 ],
            [ 3, 103.0, 206.0, 0 ],
            [ 4, 107.0, 500.0, 3 ],
            [ 101, 201.0, 0, 10 ],
        ]
        gold_c = [
            [ 2, 101.0, 202.0 ],
            [ 3, 103.0, 206.0 ],
            [ 4, 107.0, 500.0 ],
        ]
            
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )
        

    def test_acct_2addresses_daily(self):
        t = self.create_aaa()
        t.rate_mode = 'daily'
        eclients, eproviders = self.create_cp()
        eclients += [
            ['192.168.0.4', ':', 0, AAA.MEG*104, RuleId('t','c',1008)], 
            ['192.168.0.6', ':', 0, AAA.MEG*106, RuleId('t','c',1009)]
        ]
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("insert into addresses values (4, 2, '192.168.0.4', ':')")        
        t.db.sql.update("insert into addresses values (5, 3, '192.168.0.6', ':')")        
        t.db.sql.update("update users set rate = 3 where uid = 3")        
        
        debits, clients = self.create_acct(t, existed_points)
        gold_d = [
            [ 2, 101.0, 202.0, 0 ],
            [ 2, 104.0, 208.0, 0 ],
            [ 3, 103.0 , 500.0, 3 ],
            [ 3, 106.0, 0, 3 ],
            [ 101, 201.0, 402.0, 0 ],
        ]
        gold_c = [
            [ 2, 101.0, 202.0 ],
            [ 2, 104.0, 208.0 ],
            [ 3, 103.0, 500.0 ],
            [ 3, 106.0, 0.0 ],
        ]
            
        self.assertTrue( debits == gold_d )
        self.assertTrue( clients == gold_c )
       

#AUTH
    
    def test_auth_normal(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        clients_g = []
        providers_g = []
        erase_g = []
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )
        
    def test_auth_fw_missed(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        del eclients[1]
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        clients_g = [ ['192.168.0.3', '00:0E:2E:BE:46:27', 0], ]
        providers_g = []
        erase_g = []
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )
        
    def test_auth_db_missed(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        del allowed_points[1]
        
        clients_g = [ ]
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )        

    def test_auth_fw_mac(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        eclients[0][1] = '00:11:22'
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        
        clients_g = [ ['192.168.0.2', '00:04:61:A7:71:BE', 0], ]
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )
        
    def test_auth_db_mac(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        allowed_points[1].mac = '00:11:22'
        
        
        clients_g = [ ['192.168.0.2', '00:11:22', 0], ]
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )        

    def test_auth_fw_channel(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        eclients[0][2] = 3
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        
        clients_g = [ ['192.168.0.2', '00:04:61:A7:71:BE', 0], ]
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )
        
    def test_auth_db_channel(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())
        allowed_points[1].channel = 3
        
        
        clients_g = [ ['192.168.0.2', '00:04:61:A7:71:BE', 3], ]
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )

    def test_auth_nomoney(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("update users set account = -3, acctlimit = -2 where uid = '2'")
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())

        clients_g = []
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )
        
    def test_auth_traflimit(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("update users set traf = 2, traflimit = 1 where uid = '2'")
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())

        clients_g = []
        providers_g = []
        erase_g = existed_points[0].id
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )

    def test_auth_2addresses(self):
        t = self.create_aaa()
        eclients, eproviders = self.create_cp()
        existed_points = self.create_existed_points(eclients, eproviders)
        t.db.sql.update("insert into addresses values (4, 2, '192.168.0.4', '12:34')")
        allowed_points = t.get_allowed(t.get_clients(), t.get_providers())

        clients_g = [ ['192.168.0.4','12:34', 0], ]
        providers_g = []
        erase_g = []
        clients, providers, erase = self.create_auth(t, allowed_points, existed_points)
        
        self.assertTrue( clients == clients_g )
        self.assertTrue( providers == providers_g )
        self.assertTrue( erase == erase_g )


#DHCP

    def get_gold_from_doc(self, method):
        text = method.__doc__
        out = ''
        for i in text.split('\n')[1:-1]:
            out += i[8:] + '\n'
        return out

    def test_dhcp_normal(self):
        '''
        host 192_168_0_2 {
          hardware ethernet 00:04:61:A7:71:BE;
          fixed-address 192.168.0.2;
        }
        host 192_168_0_3 {
          hardware ethernet 00:0E:2E:BE:46:27;
          fixed-address 192.168.0.3;
        }
        '''
        dhcp_file = config.dhcp_config
        file(dhcp_file, 'w').write(' ')
        t = self.create_aaa()
        clients = t.get_clients()
        t.dhcp(clients)
        result = file(dhcp_file).read()
        gold = self.get_gold_from_doc(self.test_dhcp_normal)
        self.assertTrue( result == gold )

    def test_dhcp_same_file(self):
        '''
        host 192_168_0_2 {
          hardware ethernet 00:04:61:A7:71:BE;
          fixed-address 192.168.0.2;
        }
        host 192_168_0_3 {
          hardware ethernet 00:0E:2E:BE:46:27;
          fixed-address 192.168.0.3;
        }
        '''
        gold = self.get_gold_from_doc(self.test_dhcp_same_file)
        dhcp_file = config.dhcp_config
        file(dhcp_file, 'w').write(gold)
        t = self.create_aaa()
        clients = t.get_clients()
        self.assertFalse( t.dhcp(clients) )
        result = file(dhcp_file).read()
        self.assertTrue( result == gold )



if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)s %(levelname)s %(message)s')
    suite = unittest.makeSuite(Main)
    unittest.TextTestRunner(verbosity=2).run(suite)
