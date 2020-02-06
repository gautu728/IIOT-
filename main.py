"'sih main program which should start on boot to get signals and send to api'"

#importing required libraries
from datetime import datetime
import time
import RPi.GPIO as GPIO
import requests as req
import os
import sqlite3 as sqlite
from threading import Thread *
import json
from sqlalchemy import exc,cast,Date,func,and_

spindleSignalInputPin=7
runOutNotOkSignalInputPin=9
m30SignalInputPin=11
resetSignalInputPin=15
emergencySignalInputPin=14
alarmSignalInputPin=18
gcycleSignalInputPin=17
machineSignalInputPin=22
continousHighPin=13
powerFailureSignalPin=31
machineId=""
srNo=0
seqNo=0

productionArray=["cycleON","m30ON","cycleOFF","m30OFF"]
tempProductionArray=[]


#make connection with local database here
conn=sqlite.connect("erp.db");
curs=conn.cursor()
curs.execute("SELECT * FROM pinout")


for row in curs.fetchall():
    machineId=str(row[1])
    if(row[2]=="machine"):
        machineSignalInputPin= int(row[3])   
    elif(row[2]=="cycle"):
        cycleSignalInputPin=int(row[3])
    elif(row[2]=="alarm"):
        alarmSignalInputPin=int(row[3])
    elif(row[2]=="emergency"):
        emergencySignalInputPin=int(row[3])
    elif(row[2]=="reset"):
        resetSignalInputPin=int(row[3])
    elif(row[2]=="m30"):
        m30SignalInputPin=int(row[3])
    elif(row[2]=="runoutnotok"):
        runOutNotOkSignalInputPin=int(row[3])
    else:
        spindleSignalInputPin=int(row[3])
        
        
        


#setting mode of gpio pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(machineSignalInputPin,GPIO.IN)
GPIO.setup(cycleSignalInputPin,GPIO.IN)
GPIO.setup(m30SignalInputPin,GPIO.IN)
GPIO.setup(emergencySignalInputPin,GPIO.IN)
GPIO.setup(resetSignalInputPin,GPIO.IN)
GPIO.setup(alarmSignalInputPin,GPIO.IN)
GPIO.setup(runOutNotOkSignalInputPin,GPIO.IN)
GPIO.setup(spindleSignalInputPin,GPIO.IN)
GPIO.setup(powerFailureSignalPin,GPIO.IN)
GPIO.setup(continousHighPin,GPIO.OUT)
#setting warnings false 
GPIO.setwarnings(False)
GPIO.output(continousHighPin,True)


# curs.execute("select * from endpoints")
# for i in curs.fetchall():
#   url=row[1]
#   method=row[2]
# print(url)
# print(method)
  
curs.execute("SELECT count(*) FROM sequence_generator WHERE id = ?", (1,))
data=curs.fetchone()[0]

print("data : {}".format(data))
if(data==0):
   sql="INSERT INTO sequence_generator(status,generateNew) VALUES(?,?)"         
   value=("null","y")
   try:
     curs.execute(sql,value)
     conn.commit()
   except:
     print("failed to generate sequence id")  

else:
  curs.execute("SELECT * FROM sequence_generator ORDER BY id DESC LIMIT 1")
  seqNo=curs.fetchone()[0]
  print("using this seqId : {}".format(seqNo))
try:
     curs.execute("SELECT * FROM signals ORDER BY srNo DESC LIMIT 1")
     srNo=curs.fetchone()[1]
     conn.commit()
     print("starting from srNo : {}".format(srNo))
except:
     print("failed to fetch srNo")  




#api link
#url="http://10.130.10.100/be/api/iiot/MachineInput2"
#url="http://192.168.43.242:3000"
localServer="http://127.0.0.1:3000/HoldMachine"
header={'Content-type': 'application/json', 'Accept': 'application/json'}

#global variable used the program
cycleflag=0
spindleflag=0
resetflag=0
emergencyflag=0
alarmflag=0
runoutnotokflag=0
machineflag=0
m30flag=0
localStorageFlag=0
process=""
machineStatus=0
cycleStatus=0
m30Status=0
emergencyStatus=0
alarmStatus=0
resetStatus=0
spindleStatus=0
runOutNotOkStatus=0




print("----------------------------------------")
print(" \t main program starting  ")
print("----------------------------------------")


class getCurrentStatus:
   
   def __init__(self,InputPin,processOn,processOff):
       
         
         global cycleflag
         global spindleflag
         global runoutnotokflag
         global alarmflag
         global machineflag
         global emergencyflag
         global m30flag
         global resetflag
         global localStorageFlag
         global machineId,srNo,seqNo,conn,productionArray,tempProductionArray
         flag=int(self.getFlagStatus(processOn))
         SignalStatus=GPIO.input(InputPin)
         timeObj = datetime.now()
         timeStamp=timeObj.strftime("%Y/%m/%d %H:%M:%S")

         #machine on conditions
         if(flag == 0 and SignalStatus==1):
            srNo+=1
            if(srNo>1000):
                srNo=1
                curs.execute("SELECT * FROM sequence_generator ORDER BY id DESC LIMIT 1")
                lastid=curs.fetchone()[0]
                print("updating used for id {}".format(lastid))
                sqlUpdate="update sequence_generator set status=? where id=?"
                sql="INSERT INTO sequence_generator(status,generateNew) VALUES(?,?)"         
                value=("null","y")
                valueUpdate=("used",lastid)
                try:
                    curs.execute(sqlUpdate,valueUpdate)
                    conn.commit()
                    print("made max use of created sequence")
                except:
                    print("failed to update USED in squence trying once more.. ")
                    while(not curs.execute(sqlUpdate,valueUpdate)):
                      print("failed to update USED in squence trying once more.. ")
                      time.sleep(0.5)
                    conn.commit()   
                try:
                    curs.execute(sql,value)
                    conn.commit()
                    print("successfully created new sequence")
                except:
                    print("failed to create a sequence trying once more ")
                    while(not curs.execute(sql,value)):
                      print("trying to create sequence once more .....")
                      time.sleep(0.5)
                    conn.commit()
            sql="select * from sequence_generator order by id desc limit 1"
            curs.execute(sql)
            seqNo=curs.fetchone()[0] 
                  
            process=processOn
             
            print(process)
            print(timeStamp)
            self.setFlagStatus(process,1)
            srNo+=1
            sql="INSERT INTO signals(seqNo,srNo,machineId,process,timeStamp) VALUES(?,?,?,?,?)"               
            values=(seqNo,srNo,machineId,process,timeStamp)
            try:
              if(curs.execute(sql,values)):
                  conn.commit()
                  print("successfully inserted into local database")
                  self.setFlagStatus(process,1)
            except:
                  print("unable to insert into local database")
            
            #holding machine and comparing for production count      
            if(process=="machineON"):
                  self.machineHold("Hold")
           
            else:
                pass
             
            if(process=="cycleON"):
               print(tempProductionArray)
               print(productionArray)
               tempProductionArray=[] 
               tempProductionArray.append(process)
            elif(process=="m30ON"):
               tempProductionArray.append(process)
            else:
              pass   
                  
                                                 
                  
                 
         
         #machine off condition
         if(flag == 1 and SignalStatus == 0):
            srNo+=1
            if(srNo>1000):
                srNo=1
                curs.execute("SELECT * FROM sequence_generator ORDER BY id DESC LIMIT 1")
                lastid=curs.fetchone()[0]
                print("updating used for id {}".format(lastid))
                sqlUpdate="update sequence_generator set status=? where id=?"
                sql="INSERT INTO sequence_generator(status,generateNew) VALUES(?,?)"         
                value=("null","y")
                valueUpdate=("used",lastid)
                try:
                    curs.execute(sqlUpdate,valueUpdate)
                    conn.commit()
                    print("made max use of created sequence")
                except:
                    print("failed to update USED in squence trying once more.. ")
                    while(not curs.execute(sqlUpdate,valueUpdate)):
                      print("failed to update USED in squence trying once more.. ")
                      time.sleep(0.5)
                    conn.commit()   
                try:
                    curs.execute(sql,value)
                    conn.commit()
                    print("successfully created new sequence")
                except:
                    print("failed to create a sequence trying once more ")
                    while(not curs.execute(sql,value)):
                      print("trying to create sequence once more .....")
                      time.sleep(0.5)
                    conn.commit()
                sql="select * from sequence_generator order by id desc limit 1"
                curs.execute(sql)
                seqNo=curs.fetchone()[0]
            
            process=processOff
            self.setFlagStatus(process,0)
            print(process)
            print(timeStamp)
            sql="INSERT INTO signals(seqNo,srNo,machineId,process,timeStamp) VALUES(?,?,?,?,?)"               
            values=(seqNo,srNo,machineId,process,timeStamp)
            try:
               if(curs.execute(sql,values)):
                  conn.commit()
                  print("successfully inserted into local database")
                  self.setFlagStatus(process,0)
                  localStorageFlag=1
            except:
                  print("unable to insert into local database")
                  
                  
            if(process=="cycleOFF" or "m30OFF"):
                tempProductionArray.append(process)          
            if(productionArray==tempProductionArray):
               print("Array matched")
              #try:
               data=curs.execute("SELECT MAX(id) FROM production")
               lastId=curs.fetchone()[0]
              
               #print(lastId)
               sql="update production set status=? where id=?"
               values=("1",lastId)
               print(values)
               try:
                result=curs.execute(sql,values)
                conn.commit()
                print("updated")
               except:   
                tempProductionArray=[]
              #except:
               #print("something went wrong ")
               
               if(process=="m30OFF"):
                  self.machineHold("Hold")
 
   def machineHold(self,condition):
    global header,machineId
    time.sleep(2)
    print("holding machine")
    if(condition=="Hold"):
         res=req.post(localServer,json.dumps({"State":"Hold"}),headers=header,timeout=2)
         print(res.status_code)


             
  
  
         
   def getFlagStatus(self,process):
          global cycleflag
          global spindleflag
          global runoutnotokflag
          global alarmflag
          global machineflag
          global emergencyflag
          global m30flag
          global resetflag   
          if(process=="cycleON" or process=="cycleOFF"):
            return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
            return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
            return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
            return m30flag
          elif(process=="resetON" or process=="resetOFF"):
            return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
            return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
            return alarmflag
          else:
            return  runoutnotokflag
       
   def setFlagStatus(self,process,flag):
          global cycleflag
          global spindleflag
          global runoutnotokflag
          global alarmflag
          global machineflag
          global emergencyflag
          global m30flag
          global resetflag    
          if(process=="cycleON" or process=="cycleOFF"):
            cycleflag=flag
            return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
            spindleflag=flag
            return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
            machineflag=flag
            return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
            m30flag=flag     
            return m30flag
          elif(process=="resetON" or process=="resetOFF"):
            resetflag=flag     
            return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
            emergencyflag=flag     
            return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
            alarmflag=flag     
            return alarmflag
          else:
            runoutnotokflag=flag
            return  runoutnotokflag     


                   

#create thread for sending data to start the thread
thread1=Thread(target=sendDataToServer)
thread1.start()





#---------------------------------Objects to read signals --------------------------------



while(True):
       
       
       #object for cycle on/off signal
       cycleStatus=getCurrentStatus(cycleSignalInputPin,"cycleON","cycleOFF")
       time.sleep(0.10)
      
       #object for machine on/off signal
       machineStatus2=getCurrentStatus(machineSignalInputPin,"machineON","machineOFF")
      # time.sleep(0.10)
       #object for m30 on/off signal
       m30Status=getCurrentStatus(m30SignalInputPin,"m30ON","m30OFF")
      # time.sleep(0.10)
       #object for spindle on/off signal
       spindleStatus=getCurrentStatus(spindleSignalInputPin,"spindleON","spindleOFF")
      # time.sleep(0.10)
       #object for reset on/off signal
       resetStatus=getCurrentStatus(resetSignalInputPin,"resetON","resetOFF")
      # time.sleep(0.10)
       #object for emergency on/off signal
       emergencyStatus=getCurrentStatus(emergencySignalInputPin,"emergencyON","emergencyOFF")
      # time.sleep(0.10)
       #object for alarm on/off signal
       alarmStatus=getCurrentStatus(alarmSignalInputPin,"alarmON","alarmOFF")
      # time.sleep(0.10)
       #object for runOutNotOk on/off signal
       runoutnotokStatus=getCurrentStatus(runOutNotOkSignalInputPin,"runoutNotOkON","runoutNotOkOFF")
      # time.sleep(0.10)                       

