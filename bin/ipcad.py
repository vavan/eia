#!/usr/bin/python


import os, re, sys, logging
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config


class Link:
    def __init__(self, i_pair = ('','')):
        self.iface = i_pair[0]
        self.ipaddr = i_pair[1]
        
class LinkSet(list):
    def __init__(self, link_list):
        for i in link_list:
            self.append( Link(i) )
            
    def iface(self, value):
        for i in self:
            if value == i.iface:
                return i

    def ipaddr(self, value):
        for i in self:
            if value == i.ipaddr:
                return i


class Ipcad:
    def __init__(self):
        self.record_re = re.compile(r" (\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+(\d+)\s+(\d+|-)\s+(\d+|-)\s+(\d+)\s+(eth\d|<\?>)")
        self.date_time_re = re.compile('ipcad_(\d+)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)\.dump')
        self.dump_pat = config.ipcad_dump_path + 'ipcad_%s.dump'
        self.file_date_pat = '%y-%m-%d-%H-%M-%S'
        self.max_deep = 5
        self.wan = LinkSet( config.wan )
        self.lan = Link( config.lan )
    
    def gzip(self, dump_file):
        if not os.access(dump_file+'.gz', os.F_OK):
            os.system( 'gzip -f %s'%dump_file )

    def get_dumptime(self, account_file):
        date_time = self.date_time_re.match(os.path.basename(account_file))
        if date_time != None:
            date_time = datetime(date_time.groups())
            return date_time

    def read(self, file_name):
        lines = []
        try:
            ext = os.path.splitext(file_name)[1]
            if ext == '.gz':
                f = os.popen('gzip -cd %s'%file_name)
            else:
                f = file(file_name)
            lines = f.read()
            f.close()
        except IOError,e:
            logging.error( 'Account file can not be opened: '+file_name )
            sys.exit(1)
        return lines

    def find_outcome(self, record, neighbors):
        for i in neighbors:
            if i[1:6] == record[1:6] and i[7] == self.lan.iface:
                return i[0]

    def find_income(self, record, neighbors):
        for i in neighbors:
            if i[0] == record[0] and i[2:6] == record[2:6] and i[7] == self.lan.iface:
                return i[1]

    def parse_record(self, record, neighbors):
        link = self.wan.iface( record[7] )
        if link:
            sip = record[0]
            dip = record[1]
            ''' Account packets from external iface only '''
            if link.ipaddr == sip:
                ''' outgoing packet '''
                sip = self.find_outcome(record, neighbors)
            elif link.ipaddr == dip:
                ''' incoming packet '''
                dip = self.find_income(record, neighbors)
            else:
                #logging.error( 'Strange ext packet %s->%s'%(record[0], record[1]) )
                return None       
            
            if sip != None and dip != None:
                return (sip, dip, int(record[3]), record[7])
        return None

    def parse(self, file_name):
        lines = self.read(file_name)
        
        output = []
        records = self.record_re.findall( lines )
        for idx, record in enumerate(records):
            record = self.parse_record(record, records[idx - self.max_deep : idx + self.max_deep])
            
            if record:
                output.append( record )
                #print ">>", record
                
        return output

    def get_bytes(self):
        acct_time = datetime.now()
        to_name = self.dump_pat%acct_time.strftime(self.file_date_pat)

        os.system( 'sudo rsh 127.0.0.1 clear ip accounting > /dev/null' )
        os.system( 'sudo rsh 127.0.0.1 show ip accounting checkpoint > %s'%to_name )
        
        acct_data = self.parse(to_name)
        self.gzip(to_name)
        return (acct_time, acct_data)

    def open(self, file_name):
        acct_data = self.parse(file_name)
        acct_time = self.get_dumptime(file_name)
        return (acct_time, acct_data)
    
if __name__ == '__main__':
    config.init_log()
    Ipcad().get_bytes()
    