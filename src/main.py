import requests
import json
import os
from dotenv import load_dotenv
import pprint
import boto3

load_dotenv()

API_KEY = os.environ.get("GUARDIAN_API_KEY")

base_url = 'https://content.guardianapis.com/search'

def create_url_params():
    payload = {
        "api-key": API_KEY
    }
    search_term = input("What would you like to search for today? \n")
    date_from = input("Would you like to limit those to a specific date? \n")

    payload['q'] = search_term

    if not date_from:
        payload['from-date'] = None
    else:
        payload['from-date'] = date_from
    
    return payload

def create_sqs_reference():
    reference = input("Please give a reference for your message broker")

    return reference

 
def get_api_response():

    payload = create_url_params()
    response = requests.get(base_url, params=payload)
    data = response.json()['response']['results']

    dict_keys = ['webPublicationDate', 'webTitle', 'webUrl']
   
    result_list = [[v for k, v in dict.items() if k in dict_keys] for dict in data ]
  
    result_dict = [dict(zip(dict_keys, item)) for item in result_list]

    return result_dict


def create_sqs_queue():
    
    reference = create_sqs_reference()

    sqs_client = boto3.client('sqs')
    sqs_queue = sqs_client.create_queue(
        QueueName=reference,
        MessageRetentionPeriod=259200
    )
    return sqs_queue

def send_sqs_message():

    queue_url = create_sqs_queue()

    api_response = get_api_response()

    sqs_client = boto3.client('sqs')

    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=api_response
        )
    
    return{
        'statusCode': 200,
        'body': json.dumps(api_response)
    }
    





