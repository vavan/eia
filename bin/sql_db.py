import logging, sys
from datetime import datetime
from hashlib import md5
from main import Client, Provider, Address, Rate, TrafLimit, Device
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


### Devices ###
    def get_devices(self):
        raw_devices = self.sql.select( "select id, name, mac from devices" )
        devices = []
        if raw_devices:
            for row in raw_devices:
                devices.append( Device( *row ) )
        return devices

    def add_device(self, name, mac):
        self.sql.update("insert into devices (name, mac) values ('%s', '%s')"%(name, mac))

    def delete_device(self, id):
        self.sql.update("delete from devices where id='%s'"%(id))

### Cache ###
    def get_cache(self):
        return self.sql.select( "select mac from cache" )

    def update_cache(self, mac_list):
        self.sql.update("delete from cache")
        for i in mac_list:
            self.sql.update("insert into cache (mac) values ('%s')"%(i))


### Alive ###
    def get_alive_mac(self):
        return self.sql.select( "select mac from alive, devices where alive.device = devices.id" )

    def check_alive(self, user):
        self.sql.update("select device, time, duration from alive where user = '%s'"%(user))

    def start_alive(self, user, device, duration):
        self.sql.update("insert into alive (user, device, time, duration) values ('%s', '%s', datetime('now'), '%s')"%(user, device, duration))

    def expire_alive(self):
        self.sql.update("delete from alive where (strftime('%%s','now') - "
                        "strftime('%%s', time)) > duration")





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



