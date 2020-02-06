
from flask import Flask,request,jsonify
from flask import render_template,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import exc,cast,Date,func,and_
from werkzeug.utils import secure_filename
import requests as req
import json
from datetime import datetime
import time
#import RPi.GPIO as GPIO
import zipfile,shutil
from io import StringIO
import time


machineHoldPin=16

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(machineHoldPin,GPIO.OUT)
# GPIO.setwarnings(False)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'erp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db=SQLAlchemy(app)
    


class signals(db.Model):
      seqNo=db.Column(db.INTEGER)
      srNo=db.Column(db.INTEGER)
      machineId=db.Column(db.String)
      process=db.Column(db.String)
      timeStamp=db.Column(db.String,primary_key=True)


class pinout(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      machineId=db.Column(db.String)
      signal=db.Column(db.String)
      pin=db.Column(db.String)

class endpoints(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      endpoint=db.Column(db.String)
      method=db.Column(db.String)

class SequenceGenerator(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      status=db.Column(db.String) # used or blank
      generateNew=db.Column(db.String) # y or blank      

class production(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      operatorName=db.Column(db.String)
      jobId=db.Column(db.String)
      shift=db.Column(db.String)
      component=db.Column(db.String)
      modelName=db.Column(db.String)
      operation=db.Column(db.String)
      cycleTime=db.Column(db.String)
      inspectionStatus=db.Column(db.INTEGER)
      status=db.Column(db.INTEGER)
      timeStamp=db.Column(db.String)
      machineId=db.Column(db.String)
     
class ShiftData(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      shift=db.Column(db.String)
      fromTime=db.Column(db.String)
      toTime=db.Column(db.String)
     
class productionStatus(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      status=db.Column(db.String)
      value=db.Column(db.INTEGER)
      
      
class signalStatus(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      status=db.Column(db.String)
      srValue=db.Column(db.INTEGER)  
      seqValue=db.Column(db.INTEGER)       
      



@app.route("/operator", methods=["GET", "POST"])
def operatorScreen():
    shift=session['Shift']
    username=session['fullname']
    component=session['componentSelected']
    model=session['modelSelected']
    operation=session['operationSelected']  
    machineId=session['machineId']
    if(request.form):
       #calculate the current shift
       TimeObj=datetime.now().time()
       print("Current Time :" + str(TimeObj))
       query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
       for row in query.all():
         print("resulted rows : ")     
         if(row.id==4 or row.id==5):
            pass
         elif(row.id==1):
            print("Shift 1")
            session['Shift']=row.shift 
         elif(row.id==2):
           print("Shift 2")
           session['Shift']=row.shift 
         elif(row.id==3):
           print("Shidt 3")
           session['Shift']=row.shift                         
         else: 
           session['Shift']="Second" 
           
       optNameTemp=request.form.get('user')
       shiftTemp=request.form.get('shift')
       machineIdTemp=request.form.get('machineId')
       componentTemp=request.form.get('component')
       modelNameTemp=request.form.get('modelName')
       operationTemp=request.form.get('operation')
       jobIdTemp=request.form.get('jobId')
       #print(modelNameTemp)
       timeObj = datetime.now()
       time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
       productionObj=production(operatorName=username,jobId=jobIdTemp,shift=shift,component=component,modelName=model,operation=operation,cycleTime="5.5",inspectionStatus=0,status=0,timeStamp=time,machineId=machineId) 
       try:
           
          
           db.session.add(productionObj)
           db.session.commit()
           print("inserting into databse")
       except exc.IntegrityError:
           print("Integrity error")   
           db.session.rollback() 
       print("releasing machine")
       releaseUrl="http://127.0.0.1:3000/HoldMachine"
       headers = {'Content-type': 'application/json'}
       try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          print(res.status_code)
       except:
           print("error..")
       
       try:
             result=db.session.query(production).filter_by(status='1')
             
       except :
           print("error fetching data")
       Count=0 
       for i in result:
             Count+=1  
       return render_template('operator.html',shift=shift,user=username,machineId=machineId,components=component,models=model,productionCount=Count,operations=operation,snackBar=True)

    else:
       Count=0
       try:
             result=db.session.query(production).filter_by(status='1')
             Count=0  
             for i in result:
                Count+=1 
       except :
           print("error fetching data")
        
       return render_template('operator.html',shift=shift,user=username,machineId=machineId,components=component,models=model,productionCount=Count,operations=operation,snackBar=False)


@app.route('/setOperations', methods=['GET', 'POST'])
def setOperations():
    shift=session['Shift']
    username=session['fullname']
    component=session['component']
    model=session['model']
    machineId=session['machineId']
    if(request.form):
       #session['optSelected']=request.form.get('user')
       #session['shiftSelected']=request.form.get('shift')
       #session['machineIdSelected']=request.form.get('machineId')
       session['componentSelected']=request.form.get('componentName')
       session['modelSelected']=request.form.get('modelName')
       session['operationSelected']=request.form.get('operation')
       #print(session['modelNameSelected'])
       #print(session['operationSelected'])
       #print(session['componentSelected'])
       Count=0 
       try:
             result=db.session.query(production).filter_by(status='1')
             for i in result:
                Count+=1 
             
       except :
           print("error fetching data")
       
       return redirect(url_for('operatorScreen'))
       
       
    return render_template('setOperations.html',shift=shift,user=username,machineId=machineId,components=component,models=model)


@app.route('/login', methods=['GET', 'POST'])
def login():
   try:     
       pinoutObj=pinout.query.filter_by(id=1).first()
       machineId=pinoutObj.machineId
          
   except :
             machineId="null"
             print("failed to load")
                
   #save shift data to databse
   try:
     url="http://122.166.155.219/Project/SIH/BE/api/iiot/ShiftList"      
     res=req.get(url,timeout=2)
     datas=res.json()
     for data in datas: 
       idNew=data['ID']
       shiftNew=data['Name']
       fromTimeNew=data['FromTime']
       toTimeNew=data['ToTime']
       fromTimeNew=datetime.strptime(fromTimeNew,"%Y-%m-%dT%H:%M:%S")
       toTimeNew=datetime.strptime(toTimeNew,"%Y-%m-%dT%H:%M:%S")
       shiftObj=ShiftData(id=idNew,shift=shiftNew,fromTime=fromTimeNew,toTime=toTimeNew)
       try:
          result=ShiftData.query.filter_by(id=idNew).scalar() 
          if(result):
             pass

          else:    
            db.session.add(shiftObj)
            db.session.commit() 
            print("added shift data to datbase") 
       except exc.IntegrityError:
          db.session.rollback() 
   except:
       print("something went wrong while getting shift data...." )         
   
   
   #calculate the current shift
   TimeObj=datetime.now().time()
   print("Current Time :" + str(TimeObj))
   query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
   for row in query.all():  
     if(row.id==4 or row.id==5):
            pass
     elif(row.id==1):
            print("Shift 1")
            session['Shift']=row.shift 
            
     elif(row.id==2):
         print("Shift 2")
         session['Shift']=row.shift 
     elif(row.id==3):
         print("Shidt 3")
         session['Shift']=row.shift                         
     else: 
       session['Shift']="Second" 
       
       
        
   if(request.form):
         
       loginUrl="http://122.166.155.219/Project/SIH/BE/api/iiot/Login"
       headers = {'Content-type': 'application/json'}  
       username=request.form.get('username')
       password=request.form.get('password')
       
       if(username=="adminGautam" and password=="sih@password"):
           return render_template('homeConf.html')
       else:
           pass 
           
              
       try:
         res=req.post(loginUrl,headers=headers,data=json.dumps({"UserID":username,"Password":password,"MachineCode":machineId}),timeout=2)     
         #res=req.post("http://192.168.1.11/Project/SIH/BE/api/iiot/Login?userId=admin&passWord=passme%234&machineCode=HMD",headers=headers,timeout=3)
         #print(res.status_code)
         #if(res.status_code>=200 and res.status_code<=206):
         componentList=[]
         modelList=[]
         data=res.json()
         if(data['Error']!=None):
              print("error")    
              return render_template('login.html',machineId=machineId,status=data['Error']) 
         else:
              session['fullname']=data['FullName']
              data1=data['Components']
              data2=data['ProductModels']
              #print(data2)
              for datas in data1:
                 componentList.append(datas['Code'])
              
          
              for datas in data2:
                 modelObj={}
                 modelObj['code']=datas['Code']
                 modelObj['value']=datas['Value']   
                 modelList.append(modelObj)       
              
              session['component']=componentList
              session['model']=modelList
              pinoutObj=pinout.query.filter_by(id=1).first()
              session['machineId']=machineId
              return redirect(url_for('setOperations'))
       
       except:
         print("error while connecting to server for login details")
         return render_template('login.html',machineId=machineId,status="Server down..please try again")
             
       
                          
       
       
   else:
      return render_template('login.html',machineId=machineId,status="null")   




         
   
@app.route('/', methods=['GET', 'POST'])
def loadScren():
   parentPath=os.path.abspath(os.path.dirname(__file__))
   childPath="templates"
   path=os.path.join(parentPath,childPath)
   try:
     os.mkdir(path)
   except:
       print("file already exits")
       
       
   url="http://122.166.155.219/Project/SIH/BE/api/iiot/GetCodeFiles"
   try:
     result=req.get(url,stream=True)
     if(result.status_code==200):
         print("succesffully received")
         z=zipfile.ZipFile(StringIO(result.content))
         for file in z.namelist():
             
           z.extract(file)
           if(file=='operator.html'):
             print("html file saving to specific folder")  
             os.path.join(os.path.dirname(__file__),'Templates')
             TemplatePath="templates"
             shutil.move(os.path.join(os.path.dirname(__file__),file),os.path.join(TemplatePath,file))
             print("done...")
           else:
               print("not html file")
                  
         
           
   except Exception as e:
         print(e)
         return render_template('loadingscreen.html')
       
         
   return render_template('loadingscreen.html')

@app.route('/shutdown', methods=['GET', 'POST'])
def shutdown():
   print("shutting down")   
   os.system("sudo shutdown -h now ") 
   return("",204)


@app.route('/HoldMachine', methods=['POST'])
def hold_machine():
    data=request.get_json()
    state=data['State']
    if(state=='Hold'):
          # holding the machine
        print("holding machine....")
        # GPIO.output(machineHoldPin,True)
    elif(state=='Release'):
          # holding the machine
          print("releasing machine....")   
          # GPIO.output(machineHoldPin,False)
    else:
          pass       
    return ("",204)
#     
#     
# #   


@app.route('/networkConf', methods=['GET', 'POST'])
def network():
  if(request.form):
       ip=request.form.get('ip')
       dns1=request.form.get('dns1')
       dns2=request.form.get('dns2')
       gateway=request.form.get('gateway')
       print(ip,dns1,dns2,gateway)
        

@app.route('/apiConf', methods=['GET', 'POST'])
def api():
   if(request.form):
       api1=request.form.get('api1')
       
       print(api1)

@app.route('/pinConf', methods=['GET', 'POST'])
def pinconf():
   if(request.form):
       pin1=request.form.get('machine')
       pin2=request.form.get('spindle')
       pin3=request.form.get('alarm')
       pin4=request.form.get('m30')
       pin5=request.form.get('cycle')
       pin6=request.form.get('reset')
       pin7=request.form.get('emergency')
       pin8=request.form.get('runoutnotok') 
       print(pin1,pin2,pin3,pin4)
   



@app.route('/signalsData', methods=['POST'])
def signalsData():
   #data=request.get_json()
   #print(data)
   #seq=data['SeqNo']
   #srNo=data['SrNo']
   #pageCount=data['PageCount']
   #print(seq)
   #print(srNo)
   #print(pageCount)
   #result=db.session.query(signals).filter_by(seqNo=1)
   #print(result[0])
   #data=result[0]
   #if(data==0):
   #    productionStatusObj=productionStatus(id=1,status="y",srValue=1,seqValue=1)
   #    try:   
   #      db.session.add(productionStatusObj)
   #      db.session.commit()
   #    except exc.IntegrityError:
   #        db.session.rollback()
   #else:
   #    try:
   #        result=db.session.query(signalStatus).first()
    #   except:
    #          print("something wrong in query") 
   #seqTemp=result[0] 
   #srTemp=result[1] 
   #try:
   #      results=db.session.query(signals).filter(signals.seqNo>=seqTemp,signals.srNo>=srTemp)
   #      for i in results:
   #         machineId=i[2]
   #         seqNo=i[0]
   #         srNo=i[1]
   #         process=i[3]
   #         timeStamp=i[4] 
   #         try:  
   #            res=req.get("192.168.1.10/Projects/SIH/BE/api/iiot/MachineInput2?" +"machineId="+machineId+"&process="+process+"&timeStamp="+timeStamp+"&seqNo="+seqNo,timeout=1)
   #            if(res.status_code>=200 and res.status_code<=206):
   #                    result=db.session.query(signalStatus).first()
   #                    result.srValue=srNo
    #                   result.seqValue=seqNo
   #                    db.session.commit()                          
   #         except:
   #               break                 
      
   #count=0
   #for i in result:
   #      if(count>pageCount):
   #            break
   #      
   #      if(i.srNo>=srNo):
   #            count+=1
   #            resulteData.append(i)
   pass          
         
@app.route('/getOperations/<machineId>/<modelCode>', methods=['GET', 'POST'])

def getOperations(machineId,modelCode):
  try:
    url="http://122.166.155.219/Project/SIH/BE/api/iiot/OperationList?"+"machineCode="+machineId+"&modelCode="+modelCode
    response=req.get(url,timeout=3)
    OperationsList=[]       
    for res in response.json():
        operationObj = {}
        operationObj['code'] = res['Code']
        operationObj['operations'] = res['Value']
        OperationsList.append(operationObj)

    return jsonify({'operations' : OperationsList})
  except:
    return jsonify({"Message":"Error"})
      

@app.route('/tempRelease', methods=['GET', 'POST'])
def tempRelease():
    print("releasing machine")
    releaseUrl="http://127.0.0.1:3000/HoldMachine"
    headers = {'Content-type': 'application/json'}
    try:
       res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
       print(res.status_code)
    except:
       print("error..")
    return ("",204)      
   


if __name__ == "__main__":
    app.run(debug=True,port=3000,host="0.0.0.0",threaded=True)
