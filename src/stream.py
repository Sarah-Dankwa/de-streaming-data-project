import re._compiler
import requests
import requests.exceptions
import json
import re
import boto3
from botocore.exceptions import ClientError
import logging
import time
from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional

logger = logging.getLogger()

logging.getLogger().setLevel(logging.INFO)

base_url = "https://content.guardianapis.com/search"


class GuardianApiInfo(BaseModel):
    """This is the Pydantic base model for the event being passed to the lambda
       handler.
       This function ignores incorrect keys and checks for missing key

       Returns:
            The given event with validation checks
            If incorrect key is given an error message is printed.
    """
    search_term: str
    date_from: Optional[str] = None
    reference: str

    @field_validator("date_from")
    @classmethod
    def date_is_correct(cls, v):
        if v:
            if not is_valid_date(v):
                raise ValueError("Dates must be entered in the correct format")
            return v

    @field_validator("reference")
    @classmethod
    def format_reference(cls, v):
        formatted_reference = v.replace(" ", "_")
        return formatted_reference


def is_valid_date(date):
    """Checks if an inputted date is a valid year, month and year
    in the form YYYY-MM-DD
    NB. needs to be updated to ensure valid year from 1999 - 2025
    and also not a date in the future
    Returns:
        Boolean for valid or non valid dates
    """
    date_regex = re.compile(
        r"^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$")

    return bool(date_regex.match(date))


def get_api_key():
    """This function searches the aws secrets manager for the guardian api key

        Returns:
            The guardian api key in string format
    """

    secret_name = "guardian_api_key"
    secrets_client = boto3.client("secretsmanager", region_name="eu-west-2")

    try:
        get_secret_value = secrets_client.get_secret_value(
            SecretId=secret_name)
        secret = get_secret_value["SecretString"]
        secret_dict = json.loads(secret)
        return secret_dict["api_key"]

    except secrets_client.exceptions.ResourceNotFoundException as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error(f"The [{secret_name}] could not be found")


def get_api_response_json(payload):
    """This fuctions makes an api call using requests.get and a given url.

    Returns:
         The results of the api call in json format.
    """
    try:
        response = requests.get(base_url, params=payload, timeout=5)
        response.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        raise SystemExit(f'"HTTP Error:", {errh}')
    except requests.exceptions.ConnectionError as errc:
        raise SystemExit(f'"Connection Error:", {errc}')
    except requests.exceptions.Timeout as errt:
        raise SystemExit(f'"Timeout Error:",{errt}')
    except requests.exceptions.RequestException as err:
        raise SystemExit(f'"Sorry there seems to be an issue:",{err}')

    else:
        if response.status_code == 200:
            return response.json()["response"]["results"]


def format_api_response_message(api_result):
    """This function takes in the results from the api call made in
       another function and formats them.

    Returns:
       A json object with the relevant key value pairs extracted
       from the api results"""

    dict_keys = ["webPublicationDate", "webTitle", "webUrl"]

    result_list = [
        [v for k, v in info.items() if k in dict_keys] for info in api_result
    ]

    result_dict = [dict(zip(dict_keys, item)) for item in result_list]

    return json.dumps(result_dict)


def create_sqs_queue(reference):
    """Creates an sqs queue for the AWS user using the inputted reference.
      Messages within this queue are only allowed to persist for a
      maximum of 3 days

    Returns:
         The url of the created queue.
    """
    try:
        sqs_client = boto3.client("sqs", region_name="eu-west-2")
        sqs_queue = sqs_client.create_queue(
            QueueName=reference, Attributes={
                "MessageRetentionPeriod": "259200"}
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
        sqs_client = boto3.client("sqs", region_name="eu-west-2")

        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=formatted_message,
        )

        return sqs_response

    except ClientError as e:
        raise SystemExit(
            f'"This message could not be sent. Please contact AWS:", {e}')


def view_sqs_message(queue_url):
    """This function retrives the message sent to sqs by the user"""

    sqs_client = boto3.client("sqs", region_name="eu-west-2")
    sqs_message = sqs_client.receive_message(
        QueueUrl=queue_url, WaitTimeSeconds=20)

    time.sleep(5)
    messages = sqs_message.get("Messages", [])
    for message in messages:

        return f"{'Received message':1}: {message['Body']}"


def lambda_handler(event: dict, context=None):
    """
    The lambda function checks for an api-key environment variable.

    If one is present then:

        1. Url parameters are created with user input

        2. If the parameters object is the correct length then the api
           is called using requests.get and a response returned

        3. This response is then formatted to a json object

        4. An AWS SQS Queue is then created using a user inputted
           reference value and returns a url pointing to the queue.

        5. The formatted json object and queue url are then used to
           send the message to the queue.
           This functions returns some metadata which can be used
           to verify of the message was sent successfully.

        6. The user then has the option to view the message on the screen.
    """

    try:
        info = GuardianApiInfo.model_validate(event)
    except ValidationError as e:
        return {"result": "error", "message": e.errors(include_url=False)}

    api_key = get_api_key()

    payload = {"api-key": api_key, "q": info.search_term,
               "from-date": info.date_from}

    api_response = get_api_response_json(payload=payload)

    if not api_response:
        logger.error("THE API RESPONSE COULD NOT BE PROCESSED")
    formatted_response = format_api_response_message(api_response)

    queue_reference = info.reference

    sqs_queue_url = create_sqs_queue(queue_reference)

    send_sqs = send_sqs_message(formatted_response, sqs_queue_url)

    if not send_sqs["MD5OfMessageBody"]:
        logger.error("MESSAGE HAS NOT BEEN RECIEVED BY SQS")
    print("MESSAGE HAS BEEN RECIEVED BY SQS")
    logger.info("MESSAGE HAS BEEN RECIEVED BY SQS")

    view_response = view_sqs_message(sqs_queue_url)

    return view_response
