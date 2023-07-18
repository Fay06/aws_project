import boto3
import os
import json
from urllib.parse import unquote_plus
from datetime import datetime
#from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import requests
REGION = 'us-east-1'
HOST = 'search-photos-uhyk7mqxjc7wmw6diobofkww64.us-east-1.es.amazonaws.com'
INDEX = 'photos'
doc_type = '_doc'
#push version3

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)



def get_image_labels(bucket_name, image_key):
    rekognition_client = boto3.client('rekognition')

    response = rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': image_key
            }
        },
        MaxLabels=10,
        MinConfidence=90
    )

    return response['Labels']

def get_object_metadata(bucket_name, object_key):
    s3_client = boto3.client('s3')
    response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
    print('metadata:##############\n',str(response))
    created_timestamp = response.get('LastModified', None)
    cus_lable = response.get('Metadata', None)
    if cus_lable!= None:
        cus_lable = cus_lable['customlabels'].split()
    print('iCur_lable:', cus_lable)
    return created_timestamp, cus_lable

def format_timestamp(timestamp):
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S')

s3_client = boto3.client('s3')
#dynamodb = boto3.resource('dynamodb')
#table_name = 'your_dynamodb_table_name'




def lambda_handler(event, context):
    # Get the bucket and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    print('////bucket_name:', bucket_name)
    print('/////image_key:', image_key)
    #bucket_name = 'photoscloud6998'
    #image_key = 'p1.jpg'
    
    labels = get_image_labels(bucket_name, image_key)
    created_timestamp, cus_lable = get_object_metadata(bucket_name, image_key)
    
    max_id = 0
    #print('###########max_id:', max_id)
    
    
    
    auth = get_awsauth(REGION, 'es')
    
    client = OpenSearch(
    hosts = [{'host': HOST, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
    )
    index_name = 'photos'
    
    #index_body = {
    #  'settings': {
    #    'index': {
    #      'number_of_shards': 1
    #    }
    #  }
    #}
    #response = client.indices.create(index_name)
    #document = {
    #'id': 1,
    #'ObjectKey': image_key,
    #'Bucket': bucket_name,
    #'CreatedTimestamp': format_timestamp(created_timestamp),
    #'labels':[ele['Name'] for ele in labels]
    #}
    
    query = {
    "aggs" : {
      "max_id" : {
        "max" : { 
          "field" : "id"
        }
      }
    },
    "size":0
    }
    response = client.search(
    body = query,
    index = index_name
    )
    timestamp  = format_timestamp(created_timestamp)
    labels = [ele['Name'] for ele in labels]
    if cus_lable != None:
        print('cus_lable:', cus_lable)
        labels.extend(cus_lable)
    print('labels:', labels)
    
    max_id = int(response['aggregations']['max_id']['value'])
    print('###########max_id:', max_id)
    document = {
    'id': max_id + 1,
    'ObjectKey': image_key,
    'Bucket': bucket_name,
    'CreatedTimestamp':timestamp ,
    'labels':labels
    }
    
    response = client.index(
    index = index_name,
    body = document,
    id = str(max_id + 1),
    refresh = True)
    #print(f"Max value for field '{field}' in index '{index}': {max_value}")
    return {
        'statusCode': 200,
        'body': 'Picture successfully added to es index'
    }
    print(response)
#def index_file(file_key, bucket):
#    # Create or update an item in the DynamoDB table with the file_key and bucket
#    table = dynamodb.Table(table_name)
#    response = table.put_item(
#        Item={
#            'file_key': file_key,
#            'bucket': bucket
#        }
#    )
#    
    #return response
