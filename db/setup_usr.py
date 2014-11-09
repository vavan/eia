#!/usr/bin/python

import os, sys
from string import Template
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg')); import config



data = \
"""
use mysql;
INSERT INTO user (Host, User, Password) VALUES ('$host','$user', password('$pwd'));

INSERT INTO db (Host, Db, User, Select_priv, Insert_priv, Update_priv, Delete_priv, Create_priv, Drop_priv, Index_priv, Alter_priv) 
VALUES ('$host', '$database', '$user', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y');
"""

data = Template(data).substitute(config.sql_credentials)
print data    
