import os, re
import logging


class Dhcp:
    def __init__(self, filename):
        self.filename = filename
        self.re_entry = re.compile('host\s+\w+\s+{\n\s+hardware ethernet ([0-9A-F:]+);\n\s+fixed-address ([0-9.]+);\n\s*}')
    
    def parse(self):
        data = file(self.filename).read()
        addresses = self.re_entry.findall(data)
        return addresses
    
    def write(self, addresses):
        file(self.filename, 'w').write(addresses)        
		
    def restart(self):
        cmd = 'service dhcpd restart'
        logging.info( cmd )
        os.system( cmd ) 

    def serialize(self, addresses):
        out = ''
        for mac, ip in addresses:
            name = ip.replace('.', '_')
            out += 'host %s {\n'%name
            out += '  hardware ethernet %s;\n'%mac
            out += '  fixed-address %s;\n'%ip
            out += '}\n'
        self.write(out)
    


