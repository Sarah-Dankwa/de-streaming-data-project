import pytest
import json
import boto3
import os
from moto import mock_aws
from src.stream import (
    create_url_parameters,
    create_sqs_queue_reference,
    format_api_response_message,
    create_sqs_queue,
    send_sqs_message,
    view_sqs_message,
    is_valid_date,
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


class TestValidDateFromFunction:
    @pytest.mark.it("Functions returns True if from-date is in the correct format")
    def test_correct_date_format(self):
        input_date = "2023-03-09"
        response = is_valid_date(input_date)
        assert response

    @pytest.mark.it("Functions returns False if from-date is in the incorrect format")
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


class TestUrlParametersCreated:
    """update to include test that incorrect from date is not accepted?"""

    @pytest.mark.it("Search term created by user input")
    def test_get_search_term_from_user(self, monkeypatch):
        inputs = iter(["politics", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        # monkeypatch.setattr('builtins.input', lambda _: "politics")
        payload_search_term = create_url_parameters()
        assert payload_search_term["q"] == "politics"

    @pytest.mark.it("From date created if inputted by user")
    def test_get_from_date_from_user(self, monkeypatch):
        inputs = iter(["politics", "2024-01-01"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        payload_from_date = create_url_parameters()
        assert payload_from_date["from-date"] == "2024-01-01"

    @pytest.mark.it("From date is None if not inputted by user")
    def test_from_date_none(self, monkeypatch):
        inputs = iter(["politics", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        payload_from_date = create_url_parameters()
        assert payload_from_date["from-date"] is None

    @pytest.mark.it("Url parameters are stored in a dictionary")
    def test_create_url_params_returns_a_dict(self, monkeypatch):
        inputs = iter(["politics", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        payload = create_url_parameters()
        assert isinstance(payload, dict)

    @pytest.mark.it("Test that payload dictionary has correct keys")
    def test_payload_has_correct_keys(self, monkeypatch):
        inputs = iter(["politics", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        payload_keys = ["api-key", "q", "from-date"]
        payload = create_url_parameters()
        expected_payload_keys = [key for key in payload]
        assert payload_keys == expected_payload_keys


class TestSQSQueueReferenceCreated:
    """tests that user creates a reference"""

    @pytest.mark.it("Reference created by user input")
    def test_get_reference_from_user(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "content")
        reference_value = create_sqs_queue_reference()
        assert reference_value == "content"

    @pytest.mark.it("Reference formatted correctly")
    def test_reference_format(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "guardian content today")
        reference_value = create_sqs_queue_reference()
        assert reference_value == "guardian_content_today"


# class TestAPICallResponse:
#     pass

#         # TEST FOR 200 RESPONSE
#         # TEST FOR NON-200 RESPONSE IF BAD REQUEST
#         # TEST FOR CORRECT FORMAT RESPONSE
#         # mock_response = mock_get.return_value
#         # mock_response.status_code = 200
#         # mock_response.json.return_value = {"key": "value"}

#         # client = APIClient()
#         # test_url = "https://testurl.com"
#         # test_payload = {"a":"b", "c":"d", "e":"f"}

#         # result = client.get_api_response_json(test_payload)

#         # print(">>>>>>>>>>>>>>>>>", result.status_code)
#         # print(">>>>>>>>>>>>>>>>>>>>", result.json())
#         # assert result.json() == {"key": "value"}
#         # assert result.status_code == 200
#         # mock_get.assert_called_once_with(test_url)

#         # test_payload = {"a":"b", "c":"d", "e":"f"}
#         # test_base_url = "https://baseurl.com"

#         # test_api_call = get_api_response_json(test_payload)

#         # monkeypatch.setattr(requests, 'get', test_base_url, test_payload)

#         # print(test_api_call)
#         # assert False


class TestAPIMessageFormat:
    @pytest.mark.it(
        "Test that each element of the formatted response is the correct length "
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

        formatted_test_api_result = format_api_response_message(test_api_result)

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

        formatted_test_api_result = format_api_response_message(test_api_result)

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

        formatted_test_api_result = format_api_response_message(test_api_result)

        assert json.loads(formatted_test_api_result)


class TestSQSQueueCreated:
    @pytest.mark.it("Test AWS SQS queue url created with given reference")
    @mock_aws
    def test_sqs_queue_url_created_accurately(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "guardian content today")
        test_reference = create_sqs_queue_reference()
        test_url = create_sqs_queue(test_reference)
        assert test_url.rsplit("/", 1)[-1] == "guardian_content_today"


class TestSQSMessageSent:
    @pytest.mark.it("Test that sqs message is sent successfully")
    @mock_aws
    def test_sqs_message_sent_successfully(self, monkeypatch):

        monkeypatch.setattr("builtins.input", lambda _: "test_content")
        test_reference = create_sqs_queue_reference()
        test_url = create_sqs_queue(test_reference)
        test_message = "This is a test"
        test_send = send_sqs_message(test_message, test_url)
        assert test_send["MD5OfMessageBody"]
        assert test_send["MessageId"]


class TestViewingSQSMessage:
    @pytest.mark.it("Test that sqs message can be viewed by user")
    @mock_aws
    def test_sqs_message_viewed_successfully(self, monkeypatch):

        monkeypatch.setattr("builtins.input", lambda _: "test_content")
        test_reference = create_sqs_queue_reference()
        test_url = create_sqs_queue(test_reference)
        test_message = "This is a test"
        send_sqs_message(test_message, test_url)

        monkeypatch.setattr("builtins.input", lambda _: "y")

        test_message = view_sqs_message(test_url)
        assert test_message == "Received message: This is a test"

    @pytest.mark.it("Test that sqs message is not viewed if decided by user")
    @mock_aws
    def test_sqs_message_not_viewed(self, monkeypatch):

        monkeypatch.setattr("builtins.input", lambda _: "test_content")
        test_reference = create_sqs_queue_reference()
        test_url = create_sqs_queue(test_reference)
        test_message = "This is a test"
        send_sqs_message(test_message, test_url)

        monkeypatch.setattr("builtins.input", lambda _: "n")

        test_message = view_sqs_message(test_url)
        assert test_message == "Thank you"
