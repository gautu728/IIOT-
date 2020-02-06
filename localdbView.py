import sqlite3
from time import sleep
conn=sqlite3.connect("LocalDatabase.db")
c=conn.cursor()
while(1):
  sleep(5)  
  c.execute("select * from signals")
  for i in c.fetchall():
     print(i)
    
