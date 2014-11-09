import os, re, sys, logging
import config
from firewall import BILLABLE, BILLABLE_I, BILLABLE_O, CHANNEL


class RuleId:
    def __init__(self, table, chain, num):
        self.table = table
        self.chain = chain
        self.num = num
    def dec(self):
        self.num -= 1
    def __lt__(self, another):
        return self.num < another.num
    def __str__(self):
        return '%s.%s.%s'%(self.table, self.chain, self.num)

class PhysicalRule:
    rule_re = re.compile(r"(\d+)\s+\d+\s+(\d+)\s+(\w+)\s+all\s+--\s+([a-z0-9*!]+)"
                         "\s+([a-z0-9*!]+)\s+([0-9./]+)\s+([0-9./]+)\s+"
                         "(?:MAC\s+([0-9A-F:]+))?"
                         "(?:MARK xset ([xX0-9a-fA-F]+)/0xf+)?")
                         
    @staticmethod
    def findall(data):
        return PhysicalRule.rule_re.findall(data)

    def __init__(self, table, chain, arg):
        num, self.bytes, self.action, sif, dif, \
            sip, dip, self.mac, self.channel = arg
        num = int(num)
        self.id = RuleId(table, chain, num)
        self.channel = self.__validate_channel(self.channel)
        self.ip = self.__validate_ip(sip, dip)
        self.iface = self.__validate_iface(sif, dif)

    def __validate_channel(self, channel):
        if channel != '':
            return int(channel, 0)
        else:
            return 0

    def __validate_ip(self, sip, dip):
        if sip != '0.0.0.0/0':
            return sip
        else:
            return dip

    def __validate_iface(self, sif, dif):
        if sif != config.lan:
            return sif
        else:
            return dif

class PhysicalRuleList(dict):
    
    def add(self, rule):
        key = '%s.%s'%(rule.id.table, rule.id.chain)
        if key not in self:
            self[key] = []
        self[key].append(rule)
        
    def get(self, table, chain):
        key = '%s.%s'%(table, chain)
        if key in self:
            return self[key]
        else:
            return []
    
class PhysicalRuleBuilder:

    def __init__(self, firewall):
        self.firewall = firewall
        self.rules = PhysicalRuleList()
    
    def build_physical_rules(self, table):
        raw_chains = self.firewall.parse_cains(table)
        for chain, rules in raw_chains:
            rules = PhysicalRule.findall(rules)
            for r in rules:
                r = PhysicalRule(table, chain, r)
                if table == CHANNEL[0]:
                    r.bytes = 0
                self.rules.add( r )
    
    def build(self):
        self.build_physical_rules(BILLABLE[0])
        self.build_physical_rules(CHANNEL[0])

    def get_client_rules(self):
        rule_map =  self.rules.get(*BILLABLE)
        rule_map += self.rules.get(*CHANNEL) 
        return rule_map
    
    def get_providers_rules(self):
        rule_map  = self.rules.get(*BILLABLE_I)
        rule_map += self.rules.get(*BILLABLE_O)
        return rule_map
        

 

