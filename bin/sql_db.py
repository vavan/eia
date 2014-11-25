import logging, sys
from datetime import datetime
from hashlib import md5
from main import Client, Device
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
        return self.sql.select("select name from admins where uid = '%s'"%(uid))[0]

    def update_admin(self, name, passwd, uid):
        if passwd:
            passwd = ",passwd=MD5('%s')"%passwd
        self.sql.update("update admins set name='%s'%s where uid = '%s'"%(name, passwd, uid))

    def set_admin_time(self, uid, time):
        self.sql.update("update admins set time='%s' where uid = '%s'"%(time, uid))

    def get_admin_time(self, uid):
        return self.sql.select("select time from admins where uid = '%s'"%(uid))[0][0]


### Clients ###

    def add_client(self):
        self.sql.update("insert into users (name, passwd, account) values ('', '', 0)")
        return self.sql.insert_id()

    def delete_client(self, uid):
        self.sql.update("delete from users where uid = '%s'"%uid)
        return self.sql.insert_id()

    def get_clients(self):
        raw_clients = self.sql.select("select uid, name, account, super from users")
        clients = []
        for c in raw_clients:
            clients.append( Client(*c) )
        return clients

    def get_client(self, uid):
        c = self.sql.select("select uid, name, account, super from users where uid='%s'"%uid)
        c = c[0]
        return Client( *c )
            
    def get_client_by_name(self, name):
        c = self.sql.select("select uid, name, account, super from users where name='%s'"%name)
        c = c[0]
        return Client( *c )
            
    def update_client_account(self, uid, debit):
        self.sql.update("update users set account = account - %f "
                "where uid = %s"%(debit, uid))

    def add_money(self, uid, money):
        self.sql.update( "update users set account = account + %f "
                "where uid = %s"%(money, uid) )

    def modify_client(self, uid, name, passwd):
        if passwd != '':
            passwd = ", passwd = '%s'"%passwd
        self.sql.update("update users set name = '%s'%s where uid = '%s'"%(name, passwd, uid))

    def set_client_time(self, uid, time):
        self.sql.update("update users set time='%s' where uid = '%s'"%(time, uid))

    def get_client_time(self, uid):
        return self.sql.select("select time from users where uid = '%s'"%(uid))[0][0]


### Devices ###
    def get_devices(self):
        raw_devices = self.sql.select( "select id, name, mac, ip from devices" )
        devices = []
        if raw_devices:
            for row in raw_devices:
                devices.append( Device( *row ) )
        return devices

    def get_device(self, device_id):
        raw_device = self.sql.select( "select id, name, mac, ip from devices where id='%s'"%device_id )
        raw_device = raw_device[0]
        return Device( *raw_device )

    def get_device_by_ip(self, ip):
        raw_device = self.sql.select( "select id, name, mac, ip from devices where ip='%s'"%ip )
        if raw_device:
            raw_device = raw_device[0]
            return Device( *raw_device )

    def add_device(self, name, mac):
        self.sql.update("insert into devices (name, mac) values ('%s', '%s')"%(name, mac))

    def update_device_ip(self, mac, ip):
        self.sql.update("update devices set ip = '%s' where mac = '%s'"%(ip, mac))

    def delete_device(self, id):
        self.sql.update("delete from devices where id='%s'"%(id))
        
    

### Cache ###
    def get_cache(self):
        return self.sql.select( "select device, mac from cache, devices where cache.device = devices.id" )

    def add_cache(self, device):
        self.sql.update("insert into cache (device) values ('%s')"%(device))

    def delete_cache(self, device):
        self.sql.update("delete from cache where device = '%s'"%(device))

### Alive ###
    def get_alives(self):
        return self.sql.select( "select device from alive" )

    def get_alive_by_user(self, user):
        return self.sql.select("select device, (duration + strftime('%%s', time) - strftime('%%s','now')) from alive where user = '%s'"%(user))

    def get_alive_by_device(self, device):
        return self.sql.select("select name from alive, users where device = '%s' and users.uid = alive.user"%(device))

    def cancel_alive(self, device):
        return self.sql.select("delete from alive where device = '%s'"%(device))

    def start_alive(self, user, device, duration):
        self.sql.update("insert into alive (user, device, time, duration) values ('%s', '%s', datetime('now'), '%s')"%(user, device, duration))

    def expire_alive(self):
        self.sql.update("delete from alive where (strftime('%s','now') - strftime('%s', time)) > duration")





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



