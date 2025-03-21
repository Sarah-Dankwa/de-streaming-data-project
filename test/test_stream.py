import pytest
import json
import boto3
from pydantic_core import ValidationError
import os
import logging
from moto import mock_aws
from unittest.mock import patch, MagicMock
import requests
from requests.exceptions import (
    Timeout,
    ConnectionError,
    HTTPError,
    RequestException
)
from src.stream import (
    GuardianApiInfo,
    format_api_response_message,
    get_api_response_json,
    create_sqs_queue,
    send_sqs_message,
    view_sqs_message,
    is_valid_date,
    get_api_key
)


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def sqs_client(aws_credentials):
    with mock_aws():
        yield boto3.client("sqs", region_name="eu-west-2")


@pytest.fixture(scope="function")
def secretsmanager_client(aws_credentials):
    secret = {"api_key": "hello"}
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(Name="guardian_api_key",
                             SecretString=json.dumps(secret))
        yield client


@pytest.fixture(scope="function")
def secretsmanager_incorrect_client(aws_credentials):
    secret = {"api_key": "hello"}
    with mock_aws():
        client = boto3.client("secretsmanager", region_name="eu-west-2")
        client.create_secret(Name="avenger_api_key",
                             SecretString=json.dumps(secret))
        yield client


class TestBaseClassValidation:
    @pytest.mark.it("Test that a non valid from date entry raises an error")
    def test_non_valid_date_from(self):
        with pytest.raises(ValueError):
            GuardianApiInfo(date_from="2024-99-04")

    @pytest.mark.it("Test that a valid from date entry returns a value date")
    def test_valid_date_from(self):
        gi = GuardianApiInfo(
            date_from="2024-01-01", search_term="politics", reference="content"
        )
        assert gi.date_from == "2024-01-01"

    @pytest.mark.it("Inputted reference is returned in the correct format")
    def test_reference_formatted(self):
        gi = GuardianApiInfo(
            reference="guardian content today",
            date_from="2024-01-01",
            search_term="politics",
        )
        assert gi.reference == "guardian_content_today"

    @pytest.mark.it("Test that a given search term is returned")
    def test_search_returned(self):
        gi = GuardianApiInfo(
            date_from="2024-01-01", search_term="politics", reference="content"
        )
        assert gi.search_term == "politics"

    @pytest.mark.it("Test that additional key is ignored")
    def test_base_model_additional_key(self):
        gi = GuardianApiInfo(
            date_from="2024-01-01", hello="goodbye",
            search_term="politics", reference="content"
        )
        assert gi == GuardianApiInfo(
            search_term='politics', date_from='2024-01-01',
            reference='content')

    @pytest.mark.it("Test that missing key raises an error")
    def test_base_model_missing_key(self):
        with pytest.raises(ValidationError):
            GuardianApiInfo(
                date_from="2024-01-01", search_term="politics"
            )

    @pytest.mark.it("Test that incorrect key raises an error")
    def test_base_model_incorrect_key(self):
        with pytest.raises(ValidationError):
            GuardianApiInfo(
                date_from="2024-01-01", search_term="politics",
                ref="content"
            )


class TestValidDateFromFunction:
    @pytest.mark.it("Returns True if from-date is in the correct format")
    def test_correct_date_format(self):
        input_date = "2023-03-09"
        response = is_valid_date(input_date)
        assert response

    @pytest.mark.it("Returns False if from-date is in the incorrect format")
    def test_incorrect_date_format(self):
        input_date = "2025-039-09"
        response = is_valid_date(input_date)
        assert not response

    @pytest.mark.it("Functions returns False if given month is incorrect")
    def test_incorrect_month_format(self):
        input_date = "2025-25-09"
        response = is_valid_date(input_date)
        assert not response

    @pytest.mark.it("Functions returns False if given day is incorrect")
    def test_incorrect_day_format(self):
        input_date = "2025-01-65"
        response = is_valid_date(input_date)
        assert not response


class TestGetApiKeyFromAWSSecretsManager:
    @pytest.mark.it("Test secret is returned as a string")
    @mock_aws
    def test_get_secret_in_correct_format(self, secretsmanager_client):
        response = get_api_key()
        assert isinstance(response, str)

    @pytest.mark.it("Correct error message if secret not found")
    @mock_aws
    def test_get_secret_error_message(self,
                                      caplog, secretsmanager_incorrect_client):
        with caplog.at_level(logging.INFO):
            get_api_key()
            assert "The [guardian_api_key] could not be found" in caplog.text


class TestGetApiCallResponseExceptions:
    @pytest.mark.it("Test for Timeout Error")
    @patch("src.stream.requests")
    def test_timeout_error(self, mock_requests):
        test_payload = {"q": "hello"}
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.side_effect = Timeout("Timeout Error")
        with pytest.raises(SystemExit):
            get_api_response_json(payload=test_payload)

    @pytest.mark.it("Test for HTTP Error")
    @patch("src.stream.requests")
    def test_http_error(self, mock_requests):
        test_payload = {"q": "hello"}
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.side_effect = HTTPError("HTTP Error")
        with pytest.raises(SystemExit):
            get_api_response_json(payload=test_payload)

    @pytest.mark.it("Test for Connection Error")
    @patch("src.stream.requests")
    def test_connection_error(self, mock_requests):
        test_payload = {"q": "hello"}
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.side_effect = ConnectionError("Connection Error")
        with pytest.raises(SystemExit):
            get_api_response_json(payload=test_payload)

    @pytest.mark.it("Test for Request Exception Error")
    @patch("src.stream.requests")
    def test_request_error(self, mock_requests):
        test_payload = {"q": "hello"}
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.side_effect = RequestException(
            "Request Exception Error")
        with pytest.raises(SystemExit):
            get_api_response_json(payload=test_payload)


class TestGetApiCallResponses:
    @pytest.mark.it("Test for correct api call response with 200 status code")
    @patch("src.stream.requests")
    def test_get_correct_response(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": {"results": "hello"}}
        mock_requests.get.return_value = mock_response

        test_payload = {"q": "hello"}

        assert get_api_response_json(payload=test_payload) == "hello"

    @pytest.mark.it("Test for api call response when status code is not 200")
    @patch("src.stream.requests")
    def test_get_bad_response(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"response": {"results": "hello"}}
        mock_requests.get.return_value = mock_response

        test_payload = {"q": "hello"}

        assert get_api_response_json(payload=test_payload) is None


class TestAPIMessageFormat:
    @pytest.mark.it(
        "Test that the formatted response is the correct length "
    )
    def test_api_response_format_length(self):

        test_api_result = [
            {
                "webPublicationDate": "value",
                "webDate": "value",
                "webTitle": "value",
                "webUrl": "value",
                "hello": "value",
            },
            {
                "webPublicationDate": "value2",
                "webHook": "value2",
                "webTitle": "value2",
                "webUrl": "value2",
                "bye": "value2",
            },
        ]

        formatted_test_api_result = format_api_response_message(
            test_api_result)

        assert len(json.loads(formatted_test_api_result)[0]) == 3
        assert len(json.loads(formatted_test_api_result)[1]) == 3

    @pytest.mark.it(
        "Test the required keys are extracted from the api response object "
    )
    def test_api_response_format_keys(self):

        test_api_result = [
            {
                "webPublicationDate": "value",
                "webDate": "value",
                "webTitle": "value",
                "webUrl": "value",
                "hello": "value",
            },
            {
                "webPublicationDate": "value2",
                "webHook": "value2",
                "webTitle": "value2",
                "webUrl": "value2",
                "bye": "value2",
            },
        ]

        dict_keys = ["webPublicationDate", "webTitle", "webUrl"]

        formatted_test_api_result = format_api_response_message(
            test_api_result)

        formatted_result_keys = [
            k for k in json.loads(formatted_test_api_result)[0].keys()
        ]

        assert formatted_result_keys == dict_keys

    @pytest.mark.it("Test the formatted response is the correct value type")
    def test_api_response_format_type(self):

        test_api_result = [
            {
                "webPublicationDate": "value",
                "webDate": "value",
                "webTitle": "value",
                "webUrl": "value",
                "hello": "value",
            },
            {
                "webPublicationDate": "value2",
                "webHook": "value2",
                "webTitle": "value2",
                "webUrl": "value2",
                "bye": "value2",
            },
        ]

        formatted_test_api_result = format_api_response_message(
            test_api_result)

        assert json.loads(formatted_test_api_result)


class TestSQSQueueCreated:
    @pytest.mark.it("Test AWS SQS queue url created with given reference")
    @mock_aws
    def test_sqs_queue_url_created_accurately(self):
        test_reference = "guardian_content"
        test_url = create_sqs_queue(test_reference)
        assert test_url.rsplit("/", 1)[-1] == "guardian_content"


class TestSQSMessageSent:
    @pytest.mark.it("Test that sqs message is sent successfully")
    @mock_aws
    def test_sqs_message_sent_successfully(self):
        test_reference = "guardian_content"
        test_url = create_sqs_queue(test_reference)
        test_message = "This is a test"
        test_send = send_sqs_message(test_message, test_url)
        assert test_send["MD5OfMessageBody"]
        assert test_send["MessageId"]


class TestViewingSQSMessage:
    @pytest.mark.it("Test that sqs message can be viewed by user")
    @mock_aws
    def test_sqs_message_viewed_successfully(self, monkeypatch):

        test_reference = "guardian_content"
        test_url = create_sqs_queue(test_reference)
        test_message = "This is a test"
        send_sqs_message(test_message, test_url)

        test_message = view_sqs_message(test_url)
        assert test_message == "Received message: This is a test"
