import sqlite3 as sqlite

conn=sqlite.connect("LocalDatabase.db")
db=conn.cursor()

#reating required tables
#curs=db.execute('''CREATE TABLE signals(id INTEGER PRIMARY KEY, machineId text,process text, timeStamp text)''')
#if(curs):
#  print("table successfully created....")
    

#urs=db.execute('''CREATE TABLE signals(id int PRIMARY KEY, machineId text,process text,timeStamp text)''')

#f(curs):
 #   print("signals table is successfully created..")
    
    
#inserting values
#for i in range(8):
#    machineId="hmd-ord-2"
#    process=input("enter process name ")
#    pin=int(input("enter pin number"))
#    curs=db.execute("INSERT INTO pinout(machineId,signalType,inputPin)VALUES(?,?,?)",(machineId,process,pin))
#    if(curs):
#        conn.commit()
#        print("succesfully inserted ")
    
    
    
db.execute("SELECT * from signals")
for i in db.fetchall():
     print(i)


db.execute("delete from signals")
conn.commit()
