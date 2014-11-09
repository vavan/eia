#!/usr/bin/python

import sys, os
import unittest
import time
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../'))
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config; config.log_file = 'test.log'
from bin.sql_db import *
from bin.firewall import Firewall
from bin.point import PointBuilder, ClientPoint, ProviderPoint



class Main(unittest.TestCase):
    
    def trace(self, cmd):
        print cmd

    def read(self, cmd):
        mangle_pos = self.input.find('===mangle===')
        if cmd.startswith('-t filter'):
            raw_rules = self.input[:mangle_pos]
        else:
            raw_rules = self.input[mangle_pos:]
        return raw_rules
        
    #is it good points?
    def test1(self):
        '''
        Chain INPUT (policy ACCEPT 106 packets, 24632 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        1          42     7225 ACCEPT     all  --  lo     *       0.0.0.0/0            0.0.0.0/0
        2        1149    86852 ACCEPT     all  --  eth1   *       0.0.0.0/0            0.0.0.0/0
        3           0        0 REJECT     udp  --  !eth1  *       0.0.0.0/0            0.0.0.0/0           udp dpt:67 reject-with icmp-port-unreachable
        4           0        0 REJECT     udp  --  !eth1  *       0.0.0.0/0            0.0.0.0/0           udp dpt:53 reject-with icmp-port-unreachable
        5           0        0 ACCEPT     tcp  --  eth1   *       0.0.0.0/0            0.0.0.0/0           tcp dpt:22
        6           0        0 ACCEPT     tcp  --  eth3   *       0.0.0.0/0            0.0.0.0/0           tcp dpt:22
        7           0        0 ACCEPT     udp  --  eth1   *       0.0.0.0/0            0.0.0.0/0           udp dpt:123
        8           0        0 DROP       tcp  --  eth4   *       0.0.0.0/0            0.0.0.0/0           tcp dpts:0:1023
        9           0        0 DROP       udp  --  eth4   *       0.0.0.0/0            0.0.0.0/0           udp dpts:0:1023
        10          0        0 DROP       tcp  --  eth3   *       0.0.0.0/0            0.0.0.0/0           tcp dpts:0:1023
        11          0        0 DROP       udp  --  eth3   *       0.0.0.0/0            0.0.0.0/0           udp dpts:0:1023
        
        Chain FORWARD (policy DROP 167 packets, 49984 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        1        1973    83797 BILLABLE   all  --  *      *       192.168.0.0/24       0.0.0.0/0
        2        3762  5489064 BILLABLE   all  --  *      *       0.0.0.0/0            192.168.0.0/24
        
        Chain OUTPUT (policy ACCEPT 1622 packets, 204194 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        
        Chain BILLABLE (2 references)
        num      pkts      bytes target     prot opt in     out     source               destination
        1        1931    81848 BILLABLE_O  all  --  *      *       192.168.0.2          0.0.0.0/0           MAC 00:04:61:A7:71:BE
        2        3716  5486903 BILLABLE_I  all  --  *      *       0.0.0.0/0            192.168.0.2
        3           0        1 BILLABLE_O  all  --  *      *       192.168.0.3          0.0.0.0/0           MAC 00:0E:2E:BE:46:27
        4           0        2 BILLABLE_I  all  --  *      *       0.0.0.0/0            192.168.0.3
        
        Chain BILLABLE_I (3 references)
        num      pkts      bytes target     prot opt in     out     source               destination
        1        3716  5486903 ACCEPT     all  --  eth3   eth1    0.0.0.0/0            0.0.0.0/0
        2           0        0 ACCEPT     all  --  eth2   eth1    0.0.0.0/0            0.0.0.0/0
        
        Chain BILLABLE_O (3 references)
        num      pkts      bytes target     prot opt in     out     source               destination
        1        1931    81848 ACCEPT     all  --  eth1   eth3    0.0.0.0/0            0.0.0.0/0
        2           0        0 ACCEPT     all  --  eth1   eth2    0.0.0.0/0            0.0.0.0/0
        ===mangle===
        Chain PREROUTING (policy ACCEPT 6044 packets, 5594841 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        
        Chain INPUT (policy ACCEPT 311 packets, 23512 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        
        Chain FORWARD (policy ACCEPT 5731 packets, 5568345 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        1        1928    81704 MARK       all  --  *      *       192.168.0.2          0.0.0.0/0           MARK set 0x14
        2        3713  5482427 MARK       all  --  *      *       0.0.0.0/0            192.168.0.2         MARK set 0x14
        
        Chain OUTPUT (policy ACCEPT 302 packets, 59768 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        
        Chain POSTROUTING (policy ACCEPT 5943 packets, 5623899 bytes)
        num      pkts      bytes target     prot opt in     out     source               destination
        
        '''
        pb = PointBuilder()
        self.input = self.test1.__doc__
        Firewall.read_firewall = self.read
        Firewall.cmd_firewall = self.trace
        points = pb.build()

        gold_c = {
            '192.168.0.2':  ( '00:04:61:A7:71:BE', 0x14, 81848+5486903 ),
            '192.168.0.3':  ( '00:0E:2E:BE:46:27', 0, 1+2 ),
        }
        gold_p = {
            'eth2':  ( 0 ),
            'eth3':  ( 5486903+81848 ),
        }
       
        for i in points:
            if isinstance(i, ClientPoint):
                self.assertTrue( i.ip in gold_c )
                self.assertTrue( gold_c[i.ip][0] == i.mac  )
                self.assertTrue( gold_c[i.ip][1] == i.channel  )
                self.assertTrue( gold_c[i.ip][2] == i.bytes  )
            elif isinstance(i, ProviderPoint):
                self.assertTrue( i.iface in gold_p )
                self.assertTrue( gold_p[i.iface] == i.bytes  )




if __name__ == '__main__':
    suite = unittest.makeSuite(Main)
    unittest.TextTestRunner(verbosity=2).run(suite)
