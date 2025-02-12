import pytest 
from src.main import create_url_params, create_sqs_reference, get_api_response

class TestUserInputFunction:
    """tests for create api url parameters"""

    @pytest.mark.it("Search term created by user input")
    def test_get_search_term_from_user(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "politics")
        payload_search_term = create_url_params()
        assert payload_search_term['q'] == "politics"

    @pytest.mark.it("From date created if inputted by user")
    def test_get_from_date_from_user(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "2024-01-01")
        payload_from_date = create_url_params()
        assert payload_from_date['from-date'] == "2024-01-01"


    @pytest.mark.it("From date is None if not inputted by user")
    def test_from_date_none(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "")
        payload_from_date = create_url_params()
        assert payload_from_date['from-date'] == None

    
    @pytest.mark.it("Url parameters are stored in a dictionary")
    def test_create_url_params_returns_a_dict(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "")
        payload = create_url_params()
        assert isinstance(payload, dict)

    @pytest.mark.it("Test that payload dictionary has correct keys")
    def test_payload_has_correct_keys(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "")
        payload_keys = ["api-key", "q","from-date"]
        payload = create_url_params()
        expected_payload_keys = [key for key in payload]
        assert payload_keys == expected_payload_keys

    class TestSQSQueueReference:
        """Test that user creates a reference"""

        @pytest.mark.it("Reference created by user input")
        def test_get_reference_from_user(self, monkeypatch):
            monkeypatch.setattr('builtins.input', lambda _: "content")
            reference_value = create_sqs_reference()
            assert reference_value == "content"

    class TestCorrectApiUrlCreated:
        """"test that the base_url and payload are passed to requests to create an accurate url"""
        
        @pytest.mark.it("Test 200 HTTP response")
        def test_http_200_response(self):
            




        
        
        
        








