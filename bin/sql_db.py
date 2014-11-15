import logging, sys
from datetime import datetime
from hashlib import md5
from main import Client, Provider, Address, Rate, TrafLimit
from sql_conn import SqlConn


class DataBase:

    def __init__(self, credentials):
        self.sql = SqlConn(credentials)

### Autorization ###

    def authorize_client(self, name, pwd, ip):
        row = self.sql.select("select uid from users where name='%s' and passwd='%s'"%(name, pwd))
        if (len(row) > 0):
            return row[0][0]
        else:
            return None

    def authorize_admin(self, name, pwd, ip):
        row = self.sql.select("select uid from admins where name='%s' and MD5('%s') = passwd"%(name, pwd))
        if (len(row) > 0):
            return row[0][0]
        else:
            return None



### Session ###

    def get_session(self, ses_id, ip, timeout):
        query =  "select uid from sessions where sid='%s' and ip='%s'"%(ses_id, ip)
        row = self.sql.select(query)
        if len(row) > 0:
            return row[0][0]
        else:
            return None

    def update_sesion(self, ses_id):
        self.sql.update("update sessions set time = datetime('now') where sid='%s'"%ses_id)

    def insert_session(self, ses_id, ip, uid):
        self.sql.update("delete from sessions where ip='%s' and uid='%s'"%(ip, uid))
        self.sql.update("insert into sessions values ('%s', datetime('now'), '%s', %s)"%(ses_id, ip, uid))

    def expire_session(self, timeout):
        self.sql.update("delete from sessions where (strftime('%%s','now') - "
                        "strftime('%%s', time)) > %s"%(timeout))



### Admin ###

    def get_admin(self, uid):
        return self.sql.select("select name, ip from admins where uid = '%s'"%(uid))[0]

    def update_admin(self, name, passwd, ip, uid):
        if passwd:
            passwd = ",passwd=MD5('%s')"%passwd
        self.sql.update("update admins set name='%s', ip='%s'%s where uid = '%s'"%(name, ip, passwd, uid))

    def set_admin_time(self, uid, time):
        self.sql.update("update admins set time='%s' where uid = '%s'"%(time, uid))

    def get_admin_time(self, uid):
        return self.sql.select("select time from admins where uid = '%s'"%(uid))[0][0]


### Clients ###

    def add_client(self):
        self.sql.update("insert into users (name, passwd, account, acctlimit, traf, traflimit, rate) "
            "values ('', '', 0, 0, 0, 0, %s)"%Rate.ALLWAYS_EXIST)
        return self.sql.insert_id()

    def delete_client(self, uid):
        self.sql.update("delete from users where uid = '%s'"%uid)
        return self.sql.insert_id()

    def get_clients(self):
        raw_clients = self.sql.select("select uid, name, account, acctlimit,"
                                      "rate, rates.price, mode, traf, traflimit "
                                      "from users, rates "
                                      "where rate = rates.id")
        clients = []
        for c in raw_clients:
            client = Client( id = c[0], name = c[1],
                            account = float(c[2]), acctlimit = float(c[3]),
                            rate = Rate(id = c[4], price = float(c[5]), mode = c[6]), 
                            traf = TrafLimit(traf = float(c[7]), limit = float(c[8])) )
            clients.append( client )
        return clients

    def get_client(self, uid):
        c = self.sql.select("select uid, name, account, acctlimit,"
                            "rate, rates.price, mode, traf, traflimit "
                            "from users, rates "
                            "where rate = rates.id and uid='%s'"%uid)
        if len(c) == 1:
            c = c[0]
            return Client( id = c[0], name = c[1],
                           account = float(c[2]), acctlimit = float(c[3]),
                            rate = Rate(id = c[4], price = float(c[5]), mode = c[6]), 
                            traf = TrafLimit(traf = float(c[7]), limit = float(c[8])) )
        else:
            logging.error('Unknown or duplicate client id: %s'%uid)
            return None

    def set_traflimit(self, uid, traflimit):
        self.sql.update("update users set traflimit = %d, traf = 0 where uid=%s"%(traflimit, uid))

    def update_client_account(self, uid, mbytes, debit):
        self.sql.update("update users set traf = traf + %f, account = account - %f "
                "where uid = %s"%(mbytes, debit, uid))

    def add_money(self, uid, money, acctlimit):
        self.sql.update( "update users set account = account + %f, acctlimit = acctlimit + %f "
                "where uid = %s"%(money, acctlimit, uid) )


    def modify_client(self, uid, name, passwd, rate):
        if passwd != '':
            passwd = ", passwd = '%s'"%passwd
        self.sql.update("update users set name = '%s', rate = '%s'%s where uid = '%s'"%(name, rate, passwd, uid))


    def get_peers_by_rate(self, rate_id):
        clients = self.sql.select("select name from users where rate = '%s'"%rate_id)
        providers = self.sql.select("select name from providers where rate = '%s'"%rate_id)
        return clients + providers

    def set_client_time(self, uid, time):
        self.sql.update("update users set time='%s' where uid = '%s'"%(time, uid))

    def get_client_time(self, uid):
        return self.sql.select("select time from users where uid = '%s'"%(uid))[0][0]



### Addresses ###

    def get_addresses(self):
        raw_addresses = self.sql.select( "select addresses.uid, addresses.ip, addresses.mac "
                                        "from addresses, users where addresses.uid = users.uid" )
        addresses = []
        for i in raw_addresses:
            addresses.append( Address( uid = i[0], ip = i[1], mac = i[2] ) )
        return addresses

    def get_addresses_web(self):
        return self.sql.select( "select id, addresses.ip, addresses.mac, addresses.uid, name "
                                "from addresses, users where addresses.uid = users.uid order by addresses.uid" )

    def delete_address(self, addrid):
        self.sql.update("delete from addresses where id = '%s'"%(addrid))

    def modify_address(self, addrid, ip = '', mac = ''):
        if ip != '':
            ip = "ip = '%s'"%ip
        if mac != '':
            mac = "mac = '%s'"%mac
            if ip != '':
                mac = ' ,' + mac
        self.sql.update("update addresses set %s%s where id = '%s'"%(ip, mac, addrid))

    def add_client_addresses(self, uid):
        self.sql.update("insert into addresses (uid, ip, mac) values (%s, '', '')"%uid)

    def get_client_addresses(self, uid):
        return self.sql.select("select id, ip, mac from addresses where uid = '%s'"%uid)

    def delete_client_addresses(self, uid):
        self.sql.update("delete from addresses where uid = '%s'"%(uid))



### Providers ###

    def get_providers(self):
        raw_providers = self.sql.select("select pid, name, ip, iface, rate, rates.price, mode "
                                        "from providers, rates where rate = rates.id")
        providers = []
        for c in raw_providers:
            provider = Provider( id = c[0], name = c[1], ip = c[2], iface = c[3],
                                  rate = Rate(id = c[4], price = float(c[5]), mode = c[6]) )
            providers.append( provider )
        return providers

    def get_provider(self, pid):
        c = self.sql.select("select pid, name, ip, iface, rate, rates.price, mode "
                            "from providers, rates where rate = rates.id and pid = %s"%pid)
        if len(c) == 1:
            c = c[0]
            provider = Provider( id = c[0], name = c[1], ip = c[2], iface = c[3],
                              rate = Rate(id = c[4], price = float(c[5]), mode = c[6]) )
            return provider

    def add_provider(self):
        self.sql.update("insert into providers (name, ip, iface, rate) values ('', '', '', 1)")
        return self.sql.insert_id()

    def modify_provider(self, uid, name, ip, iface, rate):
        self.sql.update("update providers set name = '%s', ip = '%s', iface = '%s', rate = '%s' where pid = %s" \
                        %(name, ip, iface, rate, uid))

    def del_provider(self, pid):
        self.sql.update("delete from providers where pid = %s"%pid)



### Rates ###

    def get_rates(self):
        rates = []
        for i in self.sql.select("select id, price, mode from rates") :
            rates.append( Rate(id = i[0], price = i[1], mode = i[2]) )
        return rates

    def set_client_rate(self, uid, rate_id):
        self.sql.update("update users set rate = %s where uid = %d"%(rate_id, uid))

    def set_provider_rate(self, uid, rate_id):
        self.sql.update("update users set rate = %s where uid = %d"%(rate_id, uid))

    def add_rate(self, price, mode):
        self.sql.update("insert into rates (price, mode) values(%s, '%s')"%(price, mode))

    def delete_rate(self, record_id):
        self.sql.update("delete from rates where id = %s"%record_id)



### Debits ###

    def update_debits(self, uid, mbytes, debit, rate, time):
        time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.sql.update("insert into debits (uid, mbytes, debit, time, rate) values "
                        "(%s, %f, %f, '%s', %s)"%(uid, mbytes, debit, time, rate))

    def __debit_entry(self, traf_n_debit):
        traf = traf_n_debit[0]
        debit = traf_n_debit[1]
        if traf == None:
            traf = 0
        if debit == None:
            debit = 0
        return (float(traf), float(debit))

    def get_debit(self, uid, from_to):
        query = "select sum(mbytes), sum(debit) from debits where time > '%s' and time < '%s'"%from_to
        query += " and uid='%s'"%uid
        traf_n_debit = self.sql.select(query)
        if traf_n_debit and len(traf_n_debit) == 1:
            return self.__debit_entry(traf_n_debit[0])
        else:
            logging.warning('Empty debits for UID: %s'%id)


    def get_debit_history(self, uid, from_to):
        query  = "select sum(mbytes), sum(debit), left(time,10) from debits"
        query += " where time > '%s' and time < '%s'"%from_to
        query += " and uid = '%s' group by left(time,10) order by time desc"%uid
        output = self.sql.select(query)
        traf_debit_time = []
        for traf, debit, time in output:
            traf_debit_time.append( (float(traf), float(debit), time ))
        return traf_debit_time


    def get_debits(self, from_to):
        query =  "select sum(mbytes), sum(debit), uid from debits where time > '%s' and time < '%s'"%from_to
        query += " group by uid"
        traf_n_debit = self.sql.select(query)
        traf_n_debits = {}
        if traf_n_debit:
            for i in traf_n_debit:
                traf_n_debits[i[2]] = self.__debit_entry(i)
        return traf_n_debits

    def get_log(self, from_to, is_outgoing = False):
        if is_outgoing:
            direction = "uid > 100"
        else:
            direction = "uid < 100"
        query =  "select time, sum(mbytes) from debits where %s"%direction
        query += " and time > '%s' and time < '%s' group by time order by time"%from_to
        time_n_mbytes = self.sql.select(query)
        return time_n_mbytes



### Credits ###

    def update_credits(self, uid, money, paytype, admin_uid):
        self.sql.update( "insert into credits (uid, money, flag, admin_uid, time)"
            " values (%s, %f, %s, %s, NOW())"%(uid, money, paytype, admin_uid) )

    def get_credits(self, from_to):
        return self.sql.select( "select uid, sum(money) from credits where"
                                " time > '%s' and time < '%s'"
                                " group by uid"%from_to )

    def get_credits_history(self, from_to):
        return self.sql.select( "select name, money, credits.time, flag from credits, users where"
                                " credits.time > '%s' and credits.time < '%s' and"
                                " credits.uid = users.uid order by credits.time desc"%from_to )

    def get_client_credits_history(self, uid):
        return self.sql.select( "select money, time, flag from credits where"
                                " credits.uid = %s order by time desc"%uid )



### Messages ###

    def get_all_messages(self):
        return self.sql.select( "select id, time, sender, uid, msg, time from messages order by time desc" )

    def get_message_forclient(self, uid):
        return self.sql.select( "select id, time, sender, uid, msg, time from messages where uid = '%s' or uid = '*' or sender = '%s' order by time desc"%(uid, uid) )

    def add_message(self, sender, receiver, msg, time):
        self.sql.update( "insert into messages (sender, uid, time, msg) values ('%s', '%s', '%s', '%s')"%(sender, receiver, time, msg) )

    def delete_message(self, msg_id):
        self.sql.update( "delete from messages where id = '%s'"%(msg_id) )

