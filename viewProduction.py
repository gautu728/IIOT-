import sqlite3
from time import sleep
conn=sqlite3.connect("erp.db")
c=conn.cursor()
while(1):
  sleep(2)  
  c.execute("select * from production")
  for i in c.fetchall():
     print(i)