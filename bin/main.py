
''' Product Version '''
VERSION = '0.9.1'

'''
    History:
        0.3 - Traf limit added
        0.4 - Update Web Admin. Join Credits & Debits list.
            Add unlimited (monthly) support
        0.5 - Create more sutable installation
        0.6 - Multi WAN interfaces
        0.7 - Traf model, 3 screen UI, +/- for credits, messages
        0.8 - Channels, 5 screen UI (+ providers and rates)
        0.9 - new css, edit client/provider
        0.9.1 - client messages, unread mark
        0.9.2 - dhcp restart
        0.9.3 - iproute refactoring
        0.9.4 - cli manager restore
'''

import logging


class Provider:
    def __init__(self, id, ip, iface, name, rate):
        self.id = id
        self.ip = ip
        self.rate = rate
        self.name = name
        self.iface = iface

class Client:
    def __init__(self, id, name, account, acctlimit, rate, traf):
        self.id = id
        self.addresses = []
        self.name = name
        self.account = account
        self.acctlimit = acctlimit
        self.rate = rate
        self.traf = traf

class TrafLimit:
    def __init__(self, traf, limit):
        self.traf = traf
        self.limit = limit
    
class Address:
    def __init__(self, uid, ip, mac):
        self.uid = uid
        self.ip = ip
        self.mac = mac

class Rate:

    TRAFBASED = 'traf_based'
    DAILY = 'daily'
    MONTHLY = 'monthly'
    
    ALLWAYS_EXIST = 1

    def __init__(self, id, price, mode, channel = 0):
        if mode == None:
            mode = self.TRAFBASED
        self.id = id
        self.mode = mode
        self.price = price
        self.channel = int(channel)
        self.is_updated = False
        
    def apply(self, mbytes, mode):
        if mode == None:
            mode = self.TRAFBASED
        if self.mode == self.TRAFBASED:
            return mbytes * self.price
        elif self.mode == mode:
            if not self.is_updated:
                self.is_updated = True
                return self.price
        return 0
            
    def get_full_name(self, text):
        return '#%02d (%d) %s'%(int(self.id), self.channel, self.get_name(text))

    def get_name(self, text):
        if self.mode == self.TRAFBASED:
            name = text.RATE_TRAFBASED
        elif self.mode == self.DAILY:
            name = text.RATE_DAYLY
        else:
            name = text.RATE_MONTHLY
        return '%s %s'%(self.price, name)
        

class MoneyAdds:
    NORMAL = 0
    DEBT = 1
    PAYDEBT = 2
    
    def __init__(self, value):
        if type(value) == str and len(value) > 0:
            self.__type, self.__value = self.__create(value)

    def __create(self, value):
        try:
            adds = float(value)
        except:
            adds = 0.0
        adds_type = value[0]
        if adds_type == '+':
            adds_type = self.PAYDEBT
        elif adds_type == '-':
            adds_type = self.DEBT
        else:
            adds_type = self.NORMAL
        return adds_type, adds
    
    def get_type(self):
        return self.__type

    def get_value(self):
        return self.__value
    
    @staticmethod
    def type_name(_type, text):
        if _type == MoneyAdds.DEBT:
            return text.ADD_DEBT
        elif _type == MoneyAdds.PAYDEBT:
            return text.ADD_PAYDEBT
        else:
            return text.ADD_NORMAL
    
    def get_type_name(self, text):
        return MoneyAdds.type_name(self.__type, text)
    
    def apply(self):
        logging.info("Account update %.2f [%s]"%(self.__value, self.__type))
        if self.__type == self.DEBT:
            return 0, self.get_value()
        elif self.__type == self.PAYDEBT:
            return self.get_value(), self.get_value()
        else:
            return self.get_value(), 0

    
