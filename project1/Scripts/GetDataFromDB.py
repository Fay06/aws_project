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

response = table.get_item(Key={'resId' : 23})
print(response)