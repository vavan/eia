from pysqlite2 import dbapi2 as sqlite3
from hashlib import md5

def MD5_sql(t):
    return md5(t).hexdigest()
def NOW_sql():
    return time.time()
def UNIX_TIMESTAMP_sql(t):
    return t

class SqlTest:
    
    def __init__(self, dbase):
        if dbase == None:
            dbase = ':memory:'
        self.con = sqlite3.connect(dbase)
        self.con.create_function("MD5", 1, MD5_sql)
        self.con.create_function("NOW", 0, NOW_sql)
        self.con.create_function("UNIX_TIMESTAMP", 1, UNIX_TIMESTAMP_sql)

    
db = SqlTest('test_database.lite')
while(1):
    print '>',
    query = raw_input()
    if query == 'exit':
        break
    try:
        if query.startswith('>'):
            query = query[2:]
        c = db.con.cursor()
        c.execute(query)
        db.con.commit()
        result = c.fetchall()
        
        if query.upper().startswith('SELECT'):
            print ' '.join( map(lambda x: x[0], c.description) )
            for i in result:
                for j in i:
                    if type(j) == unicode:
                        print "'%s' "%str(j),
                    else:
                        print "%s "%str(j),
                print
        else:
            print result

        c.close()
        
    except Exception, e:
        print e
        


