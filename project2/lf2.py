import json
import requests
import boto3
import logging
from requests_aws4auth import AWS4Auth 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

opensearch_host = "https://search-photos-uhyk7mqxjc7wmw6diobofkww64.us-east-1.es.amazonaws.com/photos/_search?q="
index = "photos"
#version 3
def searchwithKeyWords(keywords):
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    headers = {"Content-Type": "application/json"}
    query = []
    res = []
   
    for keyword in keywords:
        keywordurl = opensearch_host + keyword
        query.append(requests.get(keywordurl,  auth=awsauth).json())
     
        
    for ele in query:
        if "hits" in ele:
            for e in ele["hits"]["hits"]:
                objectkey = e["_source"]["ObjectKey"]
                if objectkey not in res:
                    bucketname = "photoscloud6998"
                    objecturl = "https://" + bucketname + ".s3.amazonaws.com/" + objectkey
                    res.append(objecturl)
    print(res)
    return res
    

def lambda_handler(event, context):
    # get the q from event object
    print("This is event: ", event)
    print("This is context", context)
    q = event['queryStringParameters']['q']
    
    #lex bot
    client = boto3.client('lexv2-runtime')
    response = client.recognize_text(
        botId='SG0S4HORAJ',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId="test_session",
        text=q)
    print("response from lex:", response)
    print("parsing:", response["interpretations"][0]["intent"]["slots"])
    
    keywords = []
    if response["interpretations"][0]["intent"]["slots"] != None:
        keyword1 = response["interpretations"][0]["intent"]["slots"]["keyword1"]["value"]["interpretedValue"]
        if (keyword1[-1] == "s"):
            keywords.append(keyword1[:-1])
        else:
            keywords.append(keyword1)
        
        
        if (response["sessionState"]["intent"]["slots"]["keyword2"]!=None):
            keyword2 = response["interpretations"][0]["intent"]["slots"]["keyword2"]["value"]["interpretedValue"]
            if (keyword2[-1] == "s"):
                keywords.append(keyword2[:-1])
            else:
                keywords.append(keyword2)
        
        searchphotos = searchwithKeyWords(keywords)
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps(searchphotos)
        }
        
    else:
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": []
        }