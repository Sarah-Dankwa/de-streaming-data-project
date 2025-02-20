import re._compiler
import requests, requests.exceptions
import json
import os
import re
from dotenv import load_dotenv
from pprint import pprint
import boto3
from botocore.exceptions import ClientError
import logging
import time

load_dotenv()

logger = logging.getLogger()

logging.getLogger().setLevel(logging.INFO)


API_KEY = os.environ.get("GUARDIAN_API_KEY")

base_url = "https://content.guardianapis.com/search"


def is_valid_date(date):
    """Checks if an inputted date is a valid year, month and year
    in the form YYYY-MM-DD
    NB. needs to be updated to ensure valid year from 1999 - 2025
    and also not a date in the future
    Returns:
        Boolean for valid or non valid dates
    """
    date_regex = re.compile(r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$")

    return bool(date_regex.match(date))


def create_url_parameters():
    """user will input a search term for the
       api call and an optional from date.

    Returns:
         Dictionary with environment variable api key, user inputted search term
         and optional from date to be passed to the requests module
         in a different function.
         From date will be assingned to None if not inputted by user.
    """
    payload = {"api-key": API_KEY}

    search_term = ""
    date_from = ""

    while not search_term:
        search_term = input(
            "What would you like to search for today? You must enter a value \n"
        )

    payload["q"] = search_term

    date_from = input(
        "Would you like to limit those to a specific date? Input data in the form YYYY-MM-DD \
            or press enter to skip  \n"
    )

    if not date_from:
        payload["from-date"] = None

    while date_from:
        if is_valid_date(date_from):
            payload["from-date"] = date_from
            break
        else:
            print("Please enter a valid date")
            date_from = input(
                "Would you like to limit those to a specific date? \
                    Input data in the form YYYY-MM-DD or press enter to skip  \n"
            )
            continue

    return payload


def create_sqs_queue_reference():
    """User will be prompted to provide a reference for the name of their SQS queue.

    Returns:
         Inputted reference
    """
    reference = ""

    while not reference:
        reference = input(
            "Please give a reference for your message broker.\
                You must enter a value: \n"
        )

    formatted_reference = reference.replace(" ", "_")

    return formatted_reference


def get_api_response_json(payload):
    """This fuctions makes an api call using requests.get and a given url.

    Returns:
         The results of the api call in json format.
    """
    try:
        response = requests.get(base_url, params=payload, timeout=5)
        response.raise_for_status()
        return response.json()["response"]["results"]

    except requests.exceptions.HTTPError as errh:
        raise SystemExit(f'"HTTP Error:", {errh}')
    except requests.exceptions.ConnectionError as errc:
        raise SystemExit(f'"Connection Error:", {errc}')
    except requests.exceptions.Timeout as errt:
        raise SystemExit(f'"Timeout Error:",{errt}')
    except requests.exceptions.RequestException as err:
        raise SystemExit(f'"Sorry there seems to be an issue:",{err}')


def format_api_response_message(api_result):
    """This function takes in the results from the api call made in another function
       and formats them.

    Returns:
       A json object with the relevant key value pairs extracted from the api results"""

    dict_keys = ["webPublicationDate", "webTitle", "webUrl"]

    result_list = [
        [v for k, v in dict.items() if k in dict_keys] for dict in api_result
    ]

    result_dict = [dict(zip(dict_keys, item)) for item in result_list]

    return json.dumps(result_dict)


def create_sqs_queue(reference):
    """Creates an sqs queue for the AWS user using the inputted reference.
    Messages within this queue are only allowed to persist for a maximum of 3 days

    Returns:
         The url of the created queue.
    """
    try:
        sqs_client = boto3.client("sqs")
        sqs_queue = sqs_client.create_queue(
            QueueName=reference, Attributes={"MessageRetentionPeriod": "259200"}
        )

        return sqs_queue["QueueUrl"]

    except ClientError as e:
        raise SystemExit(
            f'"This SQS queue could not be created. Please contact AWS:", {e}'
        )


def send_sqs_message(formatted_message, queue_url):
    """This function sends the formatted get requests response and sends it to
     the queue created by the user.

    Returns:
         An AWS SQS response consisting of metadata
         such as the message Id and encoded message contents
    """
    try:
        sqs_client = boto3.client("sqs")

        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=formatted_message,
        )

        return sqs_response

    except ClientError as e:
        raise SystemExit(f'"This message could not be sent. Please contact AWS:", {e}')


def view_sqs_message(queue_url):

    view_message = input("Would you like to see the message? Type y or n: \n")
    

    if view_message == "y":
        sqs_client = boto3.client("sqs")
        sqs_message = sqs_client.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20)

        time.sleep(5)
        messages = sqs_message.get("Messages", [])
        for message in messages:

            return f"{'Received message':1}: {message['Body']}"

    else:
        return "Thank you"


def lambda_handler(event=None, context=None):
    """
    The lambda function checks for an api-key environment variable.

    If one is present then:

        1. Url parameters are created with user input

        2. If the parameters object is the correct length then the api is called
           using requests.get and a response returned

        3. This response is then formatted to a json object

        4. An AWS SQS Queue is then created using a user inputted reference value
           and returns a url pointing to the queue.

        5. The formatted json object and queue url are then used to
           send the message to the queue.
           This functions returns some metadata which can be used
           to verify of the message was sent successfully.

        6. The user then has the option to view the message on the screen.
    """

    if not API_KEY:
        logger.error("API KEY NOT FOUND - PLEASE CHECK")

    parameters = create_url_parameters()

    if len(parameters) == 3:
        api_response = get_api_response_json(payload=parameters)

    if not api_response:
        logger.error("THE API RESPONSE COULD NOT BE PROCESSED")
    formatted_response = format_api_response_message(api_response)

    queue_reference = create_sqs_queue_reference()

    sqs_queue_url = create_sqs_queue(queue_reference)

    send_sqs = send_sqs_message(formatted_response, sqs_queue_url)

    if not send_sqs["MD5OfMessageBody"]:
        logger.error("MESSAGE HAS NOT BEEN RECIEVED BY SQS")
    print("MESSAGE HAS BEEN RECIEVED BY SQS")
    logger.info("MESSAGE HAS BEEN RECIEVED BY SQS")

    view_response = view_sqs_message(sqs_queue_url)

    pprint.pp(view_response)
