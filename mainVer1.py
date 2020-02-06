"'sih main program which should start on boot to get signals and send to api'"

#importing required libraries
from datetime import datetime
import time
import RPi.GPIO as GPIO
import requests as req
import os
import sqlite3 as sqlite
import threading

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


#make connection with local database here
conn=sqlite.connect("LocalDatabase.db");
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

#api link
#url="http://10.130.10.100/be/api/iiot/MachineInput2"
url="http://192.168.43.242:5000/SignalsData"

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
       
         conn=sqlite.connect("LocalDatabase.db");
         curs=conn.cursor()  
         global cycleflag
         global spindleflag
         global runoutnotokflag
         global alarmflag
         global machineflag
         global emergencyflag
         global m30flag
         global resetflag
         global localStorageFlag
         global machineId
         flag=int(self.getFlagStatus(processOn))
         SignalStatus=GPIO.input(InputPin)
         #print(InputPin)
         #print(SignalStatus)
         timeObj = datetime.now()
         timeStamp=timeObj.strftime("%Y/%m/%d %H:%M:%S")

         #machine on conditions
         if(flag == 0 and SignalStatus==1):
            process=processOn
            print(processOn)
            print(timeStamp)  
            self.setFlagStatus(process,1)
            #send data to api
            
                   
            print("Server busy inserting to local database..")
            #select * from signals where not exists(select * from signals where machineId=? and process=? and timeStamp=?)
            sql="INSERT INTO signals(machineId,process,timeStamp) VALUES(?,?,?)"               
            values=(machineId,process,timeStamp)
            if(curs.execute(sql,values)):
                 conn.commit()
                 print("successfully inserted into local database")
                 self.setFlagStatus(process,1)
            else:
                  #log data to a file
                 print("unable to insert into local database")    
                 #print(response.status_code)
                 
                 
         
         #machine off condition
         if(flag == 1 and SignalStatus == 0):
            process=processOff
            self.setFlagStatus(process,0)
            print(process)
            print(timeStamp)
            # send data to api
            
               
            # insert in local storage
            print("Server busy inserting to local database..")
            sql="INSERT INTO signals(machineId,process,timeStamp) VALUES(?,?,?)"               
            values=(machineId,process,timeStamp)
            if(curs.execute(sql,values)):
               conn.commit()
               print("successfully inserted into local database")
               self.setFlagStatus(process,0)
               
               
               
                   
         
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



def powerFailure():
      while(1):
         time.sleep(2) 
         print("checking power failure status")
         powerFailureSignal=(GPIO.input(powerFailureSignalPin))
         if(powerFailureSignal==0):
             GPIO.output(continousHighPin,False)             
             time.sleep(5)
             os.system("sudo shutdown -h now ")
            
def sendDataToServer():
     conn=sqlite.connect("LocalDatabase.db");
     curs=conn.cursor()  
     while(1):
             
             print("inside sendDataFun")
             curs.execute("select * from status")
             idNo=curs.fetchone()[2]
             print(idNo)
             
             time.sleep(2)
             curs.execute("select * from signals where id>(?) group by process,timeStamp order by id asc",(idNo,))
             for row in curs.fetchall():
                id=str(row[0])
                machineId=row[1]
                process=row[2]
                timeStamp=row[3]
                print(process,timeStamp)
                
                
                try:
                   #time.sleep(1)
                   response=req.get(url+"?machineId="+machineId+"&process="+process+"&timeStamp="+str(timeStamp),timeout=1)
                    #response=req.get(url+"?machineId="+machineId+"&process="+process+"&timeStamp="+str(timeStamp),timeout=1)
                   if(response.status_code>=200 and response.status_code<=206):
                        curs.execute("update status set value=(?) where dummy=(?)",(id,"test"))
                        print("{} entry updated..").format(id)
                        conn.commit()
                        
                except req.exceptions.RequestException as e:
                     break;
                
            
                      
                                
                        
                   
def startProgram():
   conn=sqlite.connect("LocalDatabase.db");
   curs=conn.cursor() 
   while(True):
       
       
       #object for cycle on/off signal
       getCurrentStatus(cycleSignalInputPin,"cycleON","cycleOFF")
       
       time.sleep(0.01)
      
       #object for machine on/off signal
       getCurrentStatus(machineSignalInputPin,"machineON","machineOFF")
       time.sleep(0.01)
       #object for m30 on/off signal
       getCurrentStatus(m30SignalInputPin,"m30ON","m30OFF")
       time.sleep(0.01)
       #object for spindle on/off signal
       getCurrentStatus(spindleSignalInputPin,"spindleON","spindleOFF")
       time.sleep(0.01)
       #object for reset on/off signal
       getCurrentStatus(resetSignalInputPin,"resetON","resetOFF")
       time.sleep(0.01)
       #object for emergency on/off signal
       getCurrentStatus(emergencySignalInputPin,"emergencyON","emergencyOFF")
       time.sleep(0.01)
       #object for alarm on/off signal
       getCurrentStatus(alarmSignalInputPin,"alarmON","alarmOFF")
       time.sleep(0.01)
       #object for runOutNotOk on/off signal
       getCurrentStatus(runOutNotOkSignalInputPin,"runoutNotOkON","runoutNotOkOFF")
       time.sleep(0.01)                       


if __name__=="__main__":
   localDBStorage=threading.Thread(target=startProgram)
   
   serverCommunication=threading.Thread(target=sendDataToServer)
   powerFailure=threading.Thread(target=powerFailure)

   localDBStorage.start()
   serverCommunication.start()
   powerFailure.start()
   #startProgram()



