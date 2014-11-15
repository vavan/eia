import logging, sys, os
import sqlite3 as sql
from datetime import datetime
from hashlib import md5


#TODO: replace with standard
def MD5_sql(t):
    return md5(t).hexdigest()
def NOW_sql():
    return datetime.now().strftime('%Y-%m-%d %H-%M-%S')
def UNIX_TIMESTAMP_sql(t):
    return t


class SqlConn:
    def __init__(self, sql_spec):
        database = sql_spec['database']
        try:
            db_path = self.__find(database)
            self.con = sql.connect(db_path)
        except Exception, e:
            logging.error( str(e) )
            sys.exit(1)
        self.con.create_function("MD5", 1, MD5_sql)
        self.con.create_function("NOW", 0, NOW_sql)
        self.con.create_function("UNIX_TIMESTAMP", 1, UNIX_TIMESTAMP_sql)

    def __find(self, database):
        pwd = os.path.dirname(sys.argv[0])
        db_path = pwd + '/../db/' + database
        if os.path.exists(db_path):
            return db_path
        db_path = pwd + '/../../db/' + database
        if os.path.exists(db_path):
            return db_path
        raise BaseException("Can not find database: %s"%db_path)

    def select(self, query):
        logging.info( 'SQL: '+query )
        try:
            c = self.con.cursor()
            c.execute(query)
            result = c.fetchall()
            c.close()
        except Exception, e:
            logging.error( 'Query: [%s] was failed with error: %s'%(query, str(e)))
            return None
        return result

    def update(self, query):
        logging.info( 'SQL: '+query )
        try:
            c = self.con.cursor()
            c.execute(query)
            self.con.commit()
            c.close()
        except Exception, e:
            logging.error( 'Query: [%s] was failed with error: %s'%(query, str(e)))

    def insert_id(self):
        c = self.con.cursor()
        i = self.select('SELECT last_insert_rowid()')[0][0]
        return i

    def load(self, filename):
        script = file(filename).read()
        self.con.executescript(script)
        self.con.commit()

