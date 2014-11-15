import sys, os
from hashlib import md5
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg')); import config
import sqlite3 as sql

def MD5_sql(t):
    return md5(t).hexdigest()


db = config.sql['database']
if os.path.exists(db):
    os.remove(db)

script = file('setup_db.sql').read()
con = sql.connect(db)
con.create_function("MD5", 1, MD5_sql)
con.executescript(script)
con.commit()

