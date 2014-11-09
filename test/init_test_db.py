import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../'))
from bin.sql_db import *


os.remove('test_database.lite')

db = DataBase('test_database.lite', debug_mode = True, sql = SqlTest)
db.sql.load('database.sql')
