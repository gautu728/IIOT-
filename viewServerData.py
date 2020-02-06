import sqlite3
from time import sleep
conn=sqlite3.connect('serverData.db')
c=conn.cursor()
while(1):
  sleep(5)
  c.execute("select * from signal_data")
  for i in c.fetchall():
      print(i)
  sleep(2)    
