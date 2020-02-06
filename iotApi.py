from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc,cast,Date,func
from datetime import datetime
import time
import os


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'serverData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class signalData(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      machineId=db.Column(db.String)
      process=db.Column(db.String)
      timeStamp=db.Column(db.String)


@app.route('/SignalsData', methods=['GET'])
def signalsData():
   machineId=request.args['machineId']
   process=request.args['process']
   timeStamp=request.args['timeStamp']
   signalsDataObj=signalData(machineId=machineId,process=process,timeStamp=timeStamp)
   try:
         db.session.add(signalsDataObj)
         db.session.commit()
         return jsonify({"Message":"success"})  
   except exc.IntegrityError:
        db.session.rollback()
        return jsonify({"Message":"failed"})             
 
         
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
