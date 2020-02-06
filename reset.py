import sqlite3
conn=sqlite3.connect('LocalDatabase.db')
c=conn.cursor()
c.execute('update status set value=? where dummy=?',(0,'test'))
conn.commit()
conn.close()