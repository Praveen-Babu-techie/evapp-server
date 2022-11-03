
from flask import Flask, request, flash
import flask
import json
import boto3
import time

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)

AWS_ACCESS_KEY_ID = 'AKIA4DCGHA4HU44S3KG6'
AWS_SECRET_ACCESS_KEY = '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'

dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name='us-west-2')

table = dynamodb.Table('vehicle')

response = table.scan()
data = response['Items']



def intoNum(data):
    for i in data:

        i['id'] = int(i['id'])
        i['charge'] = int(i['charge'])
    data = sorted(data, key=lambda d: d['id']) 
    data = sorted(data, key=lambda d: d['charge']) 
    return data

def getAllData():
    response = table.scan()
    data = response['Items']
    data = intoNum(data)
  
    return data


@cross_origin()
@app.route('/')
def index():
    return 'Home!'


@cross_origin()
@app.route('/reset')
def reset():
    
   
    f = open('data.json')
    data = json.load(f)
    data=data['data']
    for i in data:
        response = table.put_item(Item=i)
    return {'data': "reset"}

@cross_origin()
@app.route('/getCharging')
def getCharging():
    data=getAllData()
    keyValList = ['charging']
    expectedResult = [d for d in data if d['status'] in keyValList]
    return {'data': expectedResult}


@cross_origin()
@app.route('/getAvailable')
def getAvailable():
    data=getAllData()
    keyValList = ['available']
    expectedResult = [d for d in data if d['status'] in keyValList]
    return {'data': expectedResult}


@cross_origin()
@app.route('/getNext')
def getNext():
      data=getAllData()
      keyValList = ['charge next']
      
      
      expectedResult = [d for d in data if d['status'] in keyValList]
      return {'data': expectedResult}  

@cross_origin()
@app.route('/moveNext')
def moveNext():
        args = request.args
        args = args.to_dict()
        iden = int(args['id'])
        data=getAllData()
        flag=False
        for i in data:
            if(i['id']==iden):
                flag=True
                record=i
                record['status']="charge next"
                response = table.put_item(Item=record)
                break

        return {"response":"updated"}

@cross_origin()
@app.route('/moveCharge')
def moveCharge():
        args = request.args
        args = args.to_dict()
        iden = int(args['id'])
        data=getAllData()
        flag=False
        for i in data:
            if(i['id']==iden):
                flag=True
                record=i
                record['status']="charging"
                response = table.put_item(Item=record)
                break
        return {"response":"updated"}


@cross_origin()
@app.route('/moveAvail')
def moveAvail():
        args = request.args
        args = args.to_dict()
        iden = int(args['id'])
        data=getAllData()
        flag=False
        for i in data:
            if(i['id']==iden):
                flag=True
                record=i
                record['status']="available"
                response = table.put_item(Item=record)
                break

        return {"response":"updated"}
    
    
@cross_origin()
@app.route('/updateCharge')
def updateCharge():
        args = request.args
        args = args.to_dict()
        iden = int(args['id'])
        data=getAllData()
        flag=False
        for i in data:
            if(i['id']==iden):
                flag=True
                record=i
                charge=record['charge']
                if(charge<85):
                    charge+=5
                    time=record['ttc'].replace("m","")
                    time=int(time)
                    time=time-10
                    time=str(time)+"m"
                    record['charge']=charge
                    record['ttc']=time
                # record['status']="charging"
                    response = table.put_item(Item=record)
                    break
        
        
        return {"response":"updated"}
if __name__ == '__main__':
    app.run()
