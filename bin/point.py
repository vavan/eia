from rules import PhysicalRuleBuilder
from firewall import Firewall

fw = Firewall()

class BasePoint:
    def __init__(self):
        self.firewall = fw
        self.id = []
        self.bytes = 0
    
    def set_id(self, id):
        self.id.append( id )
       
    def set_mac(self, mac):
        pass
    
    def set_channel(self, channel):
        pass
    
    def update_bytes(self, bytes):
        self.bytes += int(bytes)
        
    def erase(self, point_list):
        for id in self.id:
            self.firewall.erase(id)
            for point in point_list:
                for i in point.id:
                    if i > id:
                        i.dec()

    
class ClientPoint(BasePoint):
    
    @staticmethod
    def get_key(rule):
        return rule.ip
    
    def __init__(self, ip):
        BasePoint.__init__(self)
        self.ip = ip
        self.mac = None
        self.channel = 0
        
    def set_channel(self, channel):
        if channel:
            self.channel = int(channel)
       
    def set_mac(self, mac):
        if mac != None and self.mac == None:
            self.mac = mac
        
    def equal(self, another):
        if self.ip == another.ip and \
            self.mac == another.mac and \
            self.channel == another.channel:
                return True
        
    def add(self):
        self.firewall.add_client(self.ip, self.mac, self.channel)
        
    def __cmp__(self, a):
        if isinstance(a, self.__class__):
            if self.ip == a.ip:
                return 0
        return 1
        
    def __str__(self):
        return 'Client: %s, %s, %s'%(self.ip, self.mac, self.channel)



class ProviderPoint(BasePoint):

    @staticmethod
    def get_key(rule):
        return rule.iface
       
    def __init__(self, iface):
        BasePoint.__init__(self)   
        self.iface = iface
        
    def equal(self, another):
        if self.iface == another.iface:
                return True
        
    def add(self):
        self.firewall.add_provider(self.iface)
        
    def __cmp__(self, another):
        if isinstance(another, self.__class__):
            if self.iface == another.iface:
                return 0
        return 1
            
    def __str__(self):
        return 'Provider: %s'%(self.iface)


class PointList(list):
    def erase(self, point):
        index = self.index(point)
        self[index].erase(self)
        del self[index]


class PointBuilder:
    
    def build_points(self, the_class, phy_rules):
        points = {}
        for rule in phy_rules:
            if the_class.get_key(rule) not in points:
                point = the_class(the_class.get_key(rule))
                points[the_class.get_key(rule)] = point
            else:
                point = points[the_class.get_key(rule)]
            point.set_id(rule.id)
            point.set_mac(rule.mac)
            point.set_channel(rule.channel)
            point.update_bytes(rule.bytes)
        return points.values()

    def build(self):
        buider = PhysicalRuleBuilder(fw)
        buider.build()
        points = PointList()
        points += self.build_points( ClientPoint, buider.get_client_rules() )
        points += self.build_points( ProviderPoint, buider.get_providers_rules() )
        return points



