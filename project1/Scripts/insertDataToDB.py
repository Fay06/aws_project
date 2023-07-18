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
db = boto3.resource('dynamodb')

table = db.Table('yelp-restaurants')
types = ['Chinese', 'Japanese', 'Cafe', 'American', 'Mediterranean', 'Mexican', 'Asian', 'Italian', 'Burgers', 'Thai', 'Vegan', 'England', 'Indian', 'Russian']
index = 0
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
        
        try:
            if (('id' not in ele.keys()) or ('name' not in ele.keys()) or ('rating' not in ele.keys()) or ('location' not in ele.keys()) or ('address1' not in ele['location'].keys()) or ('zip_code' not in ele['location'].keys())):
                continue
            if ele['id'] == None or ele['location']['zip_code'] == None or ele['location']['address1'] == None or ele['name'] == None:
                continue
            if len(ele['id']) == 0 or len(ele['location']['zip_code']) == 0 or len(ele['location']['address1'])  == 0 or len(ele['name']) == 0:
                continue
            addDict['id'] = ele['id']
            addDict['type'] = cuisineType
            addDict['name'] = ele['name']
            addDict['rating'] = Decimal(str(ele['rating'] ))
            addDict['coordinates'] = {'latitude':Decimal(str(ele['coordinates']['latitude'])), 'longitude':Decimal(str(ele['coordinates']['longitude']))}
            addDict['address'] = ele['location']['address1']
            addDict['zip_code'] = ele['location']['zip_code']
            addDict['review_count'] = ele['review_count']
            addDict['insertedAtTimeStamp'] = int(time.time())
            intZipCode = int(ele['location']['zip_code'])
            if intZipCode < 10000 or intZipCode > 10282:
                continue
            if ele['id'] in idSet:
                continue
            idSet.add(ele['id'])

            addDict['resId'] = index
            table.put_item(
                    Item=addDict
                )
            #print(index)
            if index % 500 == 0:
                print(index)
        except Exception as e:
            print('failed:', e)
            index += 1
            continue
        index += 1
        #break
    print('total number:', index)
    print('done')