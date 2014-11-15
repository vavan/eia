import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg')); import config
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../bin')); import sql_conn

db = config.sql['database']
if os.path.exists(db):
    os.remove(db)
sql = sql_conn.SqlConn(config.sql)
sql.load('setup_db.sql')
