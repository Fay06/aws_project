import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Helper Functions --- """
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
 
def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')

def elicit_slot(event, slots, slot_to_elicit, message):
    response = {
        'sessionState': event['sessionState']
    }
    
    response['sessionState']['dialogAction'] = {
        'type': 'ElicitSlot',
        'slotToElicit': slot_to_elicit
    }
    
    response['sessionState']['intent']['slots'] = slots
    
    if message is not None:
        response['messages'] = [message]
    
    return response
    
    
def delegate(event, slots):
    response = {
        'sessionState': event['sessionState']
    }
    
    response['sessionState']['dialogAction'] = {
        'type': 'Delegate'
    }
    
    response['sessionState']['intent']['slots'] = slots
    
    return response


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            'isValid': is_valid,
            'violatedSlot': violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_reservation(location, cuisine, date, time, people, email):
    cuisines = ['Chinese', 'Japanese', 'Cafe', 'American', 'Mediterranean', 'Mexican', 'Asian', 'Italian', 'Burgers', 'Thai', 'Vegan', 'England', 'Indian']
    
    if location is not None and location.lower() != 'manhattan':
        return build_validation_result(False,
                                       'Location',
                                       'We do not have business in {}, would you like a different location?  '
                                       'Our most popular dining area is Manhattan'.format(location))

            
    if cuisine is not None and cuisine not in cuisines:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not have {}, would you like a different type of cuisine?  '
                                       'Our most popular cuisine is Italian'.format(cuisine))


    return build_validation_result(True, None, None)   


""" --- Main functions --- """
def dining_suggestion(intent_request, event):
    slots = get_slots(intent_request)
    location = slots['location']['value']['interpretedValue']
    cuisine = slots['cuisine']['value']['interpretedValue']
    date = slots['date']['value']['interpretedValue']
    time = slots['time']['value']['interpretedValue']
    people = slots['NumberOfPeople']['value']['interpretedValue']
    email = slots['email']['value']['interpretedValue']
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        validation_result = validate_reservation(location, cuisine, date, time, people, email)
        
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(event, slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        return delegate(event, slots)
    
    push_to_sqs(slots)
    
    response = {
        "sessionState": {
            "dialogAction": {
                "type": "Close",
            },
            "intent": {
                "name": "DiningSuggestionsIntent",
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": "You’re all set. Expect my suggestions shortly! Have a good day."
            }
        ]
    }
    
    return response
        
def push_to_sqs(slots):
    
    client = boto3.client('sqs')
    
    messageAttributes = {
        "Location": {
            "DataType": "String",
            "StringValue": slots["location"]['value']['interpretedValue']
        },
        "Cuisine": {
            "DataType": "String",
            "StringValue": slots["cuisine"]['value']['interpretedValue']
        },
        "Date": {
            "DataType": "String",
            "StringValue": slots["date"]['value']['interpretedValue']
        },
        "Time": {
            "DataType": "String",
            "StringValue": slots["time"]['value']['interpretedValue']
        },
        "NumOfPeople": {
            "DataType": "String",
            "StringValue": slots["NumberOfPeople"]['value']['interpretedValue']
        },
        "Email": {
            "DataType" : "String",
            "StringValue" : slots["email"]['value']['interpretedValue']
        }
    }

    client.send_message(
        QueueUrl = "https://sqs.us-east-1.amazonaws.com/837163409163/info",
        MessageAttributes = messageAttributes,
        MessageBody = "reservation info"
    )


""" --- Intents --- """
def dispatch(intent_request):

    intent_name = intent_request["bot"]["name"]

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningConcierge':
        return dining_suggestion(intent_request, intent_request)
        
    raise Exception('Intent with name ' + intent_name + ' not supported')
    

""" --- Main handler --- """
def lambda_handler(event, context):

    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    print(event)
    return dispatch(event)
