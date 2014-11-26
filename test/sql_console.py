#!/usr/bin/python

import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'));import config
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../bin'));from sql_conn import SqlConn

    
db = SqlConn({'database':sys.argv[1]})
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
        


