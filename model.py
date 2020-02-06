from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc,cast,Date,func
from datetime import datetime
import time
import os


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'LocalDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class signals(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      machineId=db.Column(db.String)
      process=db.Column(db.String)
      timeStamp=db.Column(db.String)

class status(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      dummy=db.Column(db.String)
      value=db.Column(db.INTEGER)

class pinout(db.Model):
      id=db.Column(db.INTEGER,primary_key=True)
      machineId=db.Column(db.String)
      signalType=db.Column(db.String)
      inputPin=db.Column(db.INTEGER)      


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')      