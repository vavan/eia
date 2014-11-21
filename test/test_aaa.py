#!/usr/bin/python

import sys, os
import time
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../'))
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config;
from bin.sql_db import *
from bin.firewall import Firewall
from bin.point import PointBuilder, ClientPoint, ProviderPoint
from bin.aaa import AAA
from bin.sql_db import DataBase, SqlTest



class TestAAA(AAA):
    def __init__(self, rate_mode, db):
        self.rate_mode = rate_mode
        self.db = DataBase(db, debug_mode = True, sql = SqlTest)
    
    def trace(self, cmd):
        print cmd

    def read(self, cmd):
        print cmd
        mangle_pos = self.input.find('===mangle===')
        if cmd.startswith('-t filter'):
            raw_rules = self.input[:mangle_pos]
        else:
            raw_rules = self.input[mangle_pos:]
        return raw_rules
        
    
    def get_existed(self, fw_input):
        pb = PointBuilder()
        self.input = fw_input
        Firewall.read_firewall = self.read
        Firewall.cmd_firewall = self.trace
        return pb.build()
    
