import boto3
from decimal import Decimal
from io import BytesIO
import json
import logging
import os
from pprint import pprint
import requests
from zipfile import ZipFile
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import time

idSet = set()
#db = boto3.resource('dynamodb')

#table = db.Table('yelp-restaurants')
types = ['Chinese', 'Japanese', 'Cafe', 'American', 'Mediterranean', 'Mexican', 'Asian', 'Italian', 'Burgers', 'Thai', 'Vegan', 'England', 'Indian', 'Russian']
index = 0
f = open('./insertOSjson.txt', 'w')
for loop in range(0, len(types)):
    num = loop

    #index = 1000 * num
    cuisineType = types[num]

    
    f = open('{0}Res.txt'.format(cuisineType), 'r')
    text = f.read()

    resList = json.loads(text) 
    #print(resList[0]['id'], resList[0]['name'], '\n', resList[0]['phone'])


    for ele in resList:
        addDict = dict()
        
        
        if (('id' not in ele.keys()) or ('name' not in ele.keys()) or ('rating' not in ele.keys()) or ('location' not in ele.keys()) or ('address1' not in ele['location'].keys()) or ('zip_code' not in ele['location'].keys())):
            continue
        if ele['id'] == None or ele['location']['zip_code'] == None or ele['location']['address1'] == None or ele['name'] == None:
            continue
        if len(ele['id']) == 0 or len(ele['location']['zip_code']) == 0 or len(ele['location']['address1'])  == 0 or len(ele['name']) == 0:
            continue
        intZipCode = int(ele['location']['zip_code'])
        if intZipCode < 10000 or intZipCode > 10282:
            continue
        if ele['id'] in idSet:
            continue
        idSet.add(ele['id'])
        #jsonDict = dict()


        jsonStr = '\{index: \{"_index": "restaurants", "_id":' +str(index) + '\}\}\n\{"resId":' + str(cuisineType) + ', "type":' + str(index) + '\n'
        f.write(jsonStr)
        #table.put_item(
        #        Item=addDict
        #    )
        #print(index)
        if index % 3 == 0:
            print(index)
            break
        
        index += 1

        #break
    print('total number:', index)
    print('done')
    break