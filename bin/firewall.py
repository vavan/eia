import os, re, sys, logging
import config


BILLABLE = ('filter', 'BILLABLE')
BILLABLE_I = ('filter', 'BILLABLE_I')
BILLABLE_O = ('filter', 'BILLABLE_O')

CHANNEL = ('mangle', 'FORWARD')

    
class Firewall:

    def __init__(self):
        self.firewall = 'sudo iptables'
        self.lan = config.lan
    
    def read_firewall(self, cmd):
        cmd = self.firewall + ' ' + cmd
        logging.debug( cmd )
        raw_rules = os.popen( cmd )
        return raw_rules.read()

    def cmd_firewall(self, cmd):
        cmd = self.firewall + ' ' + cmd
        logging.debug( cmd )
        os.system( cmd )
   
    def parse_cains(self, table = ''):
        if table != '':
            cmd = '-t %s '%table
        cmd += '-L -v -n -x --line-numbers'
        if table == BILLABLE[0]:
            cmd += ' -Z'
        data = self.read_firewall(cmd)
        chains_re = re.compile(r'Chain (\w+)')
        data = chains_re.split(data)
        return map( None, data[1::2], data[2::2] )
    
    def add_provider(self, iface):
        self.cmd_firewall( '-A %s -i %s -o %s -j ACCEPT'%(BILLABLE_O[1], self.lan, iface ) )
        self.cmd_firewall( '-A %s -i %s -o %s -j ACCEPT'%(BILLABLE_I[1], iface, self.lan ) )
    
    def add_client(self, ip, mac, channel):
        self.cmd_firewall( '-A %s -s %s -m mac --mac-source %s -j %s'% \
               (BILLABLE[1], ip, mac, BILLABLE_O[1]) )
        self.cmd_firewall( '-A %s -d %s -j %s'% \
               (BILLABLE[1], ip, BILLABLE_I[1]) )
        if channel != 0:
            self.cmd_firewall( '-t %s -A %s -s %s -j MARK --set-mark %s'% \
                   (CHANNEL[0], CHANNEL[1], ip, channel) )
            self.cmd_firewall( '-t %s -A %s -d %s -j MARK --set-mark %s'% \
                   (CHANNEL[0], CHANNEL[1], ip, channel) )
       
    def erase(self, rule_id):
        cmd =  '-t %s -D %s %s'%(rule_id.table, rule_id.chain, rule_id.num)
        self.cmd_firewall( cmd )
        