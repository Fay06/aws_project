import boto3
import json

class Decimal:
    def __init__(self, numStr):
        self.num = float(numStr)
    
client = boto3.client('lambda')
resType = 'chinese'
inputParas = {
    'type' : resType
}
response = client.invoke(
    FunctionName = 'arn:aws:lambda:us-east-1:837163409163:function:get-data-from-os',
    Payload = json.dumps(inputParas)
    )
responseStr = response['Payload'].read()
#print(responseStr)
contentDict = json.loads(json.loads(responseStr)['body'])['results'][0]
resId = contentDict['resId']

dbResponse = client.invoke(
    FunctionName = 'arn:aws:lambda:us-east-1:837163409163:function:GetItemFromDB',
    Payload = json.dumps(contentDict)
    )
dbResponseStr = json.loads(dbResponse['Payload'].read())['body']

#dbResponseStr = str.replace(dbResponseStr, '\'', '\"')
contentDict = eval(dbResponseStr)['Item']
for ele in contentDict.keys():
    print(type(contentDict[ele]))
    if type(contentDict[ele]) == type(Decimal('1')):
        print('key:', ele, 'replaced:', contentDict[ele].num)
        contentDict[ele] = contentDict[ele].num
#print(contentDict)
returnMsg = "Hello! Here's the information of the recommended restaurant:\n name:{0}, address:{1}, type:{2}".format(contentDict['name'], contentDict['address'], resType)

ses_client = boto3.client('ses')
#ses_identity = SesIdentity(ses_client)
#ses_mail_sender = SesMailSender(ses_client)
#ses_template = SesTemplate(ses_client)
email = 'hy2800@columbia.edu'
#print(ses_identity.get_identity_status(email))
test_message_text = "Hello from the Amazon SES mail demo!"
#test_message_html = "<p>Hello!</p><p>From the <b>Amazon SES</b> mail demo!</p>"
#print(f"Sending mail from {email} to {email}.")
emailMsg = {
    'Subject' : {
        'Data': 'Your Restaurant Info',
        'Charset' : 'UTF-8'
    },
    'Body':{
        'Text':{
            'Data': returnMsg,
            'Charset' : 'UTF-8'
        }
    }
}
Destination={
            "ToAddresses": [
                "yinhaoxiang42@outlook.com",
            ]
        }
ses_client.send_email(
    Source = email, Destination = Destination, Message = emailMsg)
print('done')
#print(returnMsg)
