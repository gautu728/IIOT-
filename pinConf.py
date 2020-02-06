import sqlite3
conn=sqlite3.connect("LocalDatabase.db")
c=conn.cursor()
i=1
machineId=input("enter machine id ")
while(i<=8):
    signal=input("enter signal type ")
    pin=int(input("enter pin number "))
    c.execute("insert into pinout(machineId,signalType,inputPin)values(?,?,?)",(machineId,signal,pin))
    conn.commit()