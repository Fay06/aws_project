import json
import boto3
import random
class Decimal:
    def __init__(self, numStr):
        self.num = float(numStr)
def lambda_handler(event, context):
    
    #resType = event['Cuisine']
    null = None
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='info')
    msgList = queue.receive_messages(QueueUrl = 'https://sqs.us-east-1.amazonaws.com/837163409163/info', MaxNumberOfMessages  = 10, WaitTimeSeconds = 20, AttributeNames=['All'], MessageAttributeNames=['All'])
    returnMsg = '' + str(len(msgList))
    for message in msgList:
        #if message.message_attributes is not None:
        #print(message.body)
        try:
            attrDict = message.message_attributes
            if attrDict == None:
                continue
            contentDict = {ele:(eval(str(attrDict[ele]))['StringValue']) for ele in attrDict.keys()}
            #contentDict = eval(message.body)
            if 'Cuisine' not in contentDict.keys():
                returnMsg += 'cuisine not in keys()'
                continue
                
            #resDate = ''
            resDate = contentDict['Date'] +',' if contentDict['Date']  != None else ''
            resTime = contentDict['Time'] + ',' if contentDict['Time']  != None else ''
            numOfPeople = contentDict['NumOfPeople'] + ',' if contentDict['NumOfPeople']  != None else ''
            resType = contentDict['Cuisine'] 
            emailAdd = contentDict['Email'] 
            client = boto3.client('lambda')
            
            inputParas = {
                'type' : resType
            }
            response = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:837163409163:function:get-data-from-os',
                Payload = json.dumps(inputParas)
                )
            responseStr = response['Payload'].read()
            #print(responseStr)
            tempList = json.loads(json.loads(responseStr)['body'])['results']
            if len(tempList) == 0:
                ses_client = boto3.client('ses')
                email = 'hy2800@columbia.edu'
                #test_message_text = "Hello from the Amazon SES mail demo!"
                emailMsg = {
                    'Subject' : {
                        'Data': 'Your Restaurant Info',
                        'Charset' : 'UTF-8'
                    },
                    'Body':{
                        'Text':{
                            'Data': 'Sorry, we cannot find suitable restaurant',
                            'Charset' : 'UTF-8'
                        }
                    }
                }
                Destination={
                            "ToAddresses": [
                                emailAdd,
                            ]
                        }
                ses_client.send_email(
                    Source = email, Destination = Destination, Message = emailMsg)
                returnMsg += 'failed, cannot find restaurant'
                queue.delete_messages(Entries = [{'Id':message.message_id, 'ReceiptHandle': message.receipt_handle}])
                returnMsg += 'delete done'
                continue
            contentDict = tempList[random.randint(0, len(tempList) - 1)]
            resId = contentDict['resId']
            
            dbResponse = client.invoke(
                FunctionName = 'arn:aws:lambda:us-east-1:837163409163:function:GetItemFromDB',
                Payload = json.dumps(contentDict)
                )
            dbResponseStr = json.loads(dbResponse['Payload'].read())['body']
            
            #dbResponseStr = str.replace(dbResponseStr, '\'', '\"')
            contentDict = eval(dbResponseStr)['Item']
            for ele in contentDict.keys():
                #print(type(contentDict[ele]))
                if type(contentDict[ele]) == type(Decimal('1')):
                    #print('key:', ele, 'replaced:', contentDict[ele].num)
                    contentDict[ele] = contentDict[ele].num
            #print(contentDict)
            emailMsgText = "Hello! Here's the information of the recommended restaurant:\n {0}, {1}, {2} {3} {4} {5}".format(contentDict['name'], contentDict['address'], resType, resDate, resTime, numOfPeople)
            
            ses_client = boto3.client('ses')
            email = 'hy2800@columbia.edu'
            #test_message_text = "Hello from the Amazon SES mail demo!"
            emailMsg = {
                'Subject' : {
                    'Data': 'Your Restaurant Info',
                    'Charset' : 'UTF-8'
                },
                'Body':{
                    'Text':{
                        'Data': emailMsgText,
                        'Charset' : 'UTF-8'
                    }
                }
            }
            Destination={
                        "ToAddresses": [
                            emailAdd,
                        ]
                    }
            ses_client.send_email(
                Source = email, Destination = Destination, Message = emailMsg)
            returnMsg += emailMsgText + '\n'
            queue.delete_messages(Entries = [{'Id':message.message_id, 'ReceiptHandle': message.receipt_handle}])
            returnMsg += ' delete done'
        except Exception as e:
            returnMsg += str(e)
            continue
        
    return {
        'statusCode': 200,
        'body': returnMsg
    }
