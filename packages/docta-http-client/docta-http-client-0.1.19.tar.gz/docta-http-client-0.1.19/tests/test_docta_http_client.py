import pytest
import requests_mock
import json
from src.docta_http_client.base_client import APIClient
from src.docta_http_client.models import ModelType
from src.docta_http_client import DoctaHTTPClient
from src.docta_http_client.utils import parse_json_response, check_status_code

@pytest.fixture
def docta_client():
    return DoctaHTTPClient(api_key='fake_api_key', user_id='fake_user_id')


def test_set_and_get_model(docta_client):
    docta_client.set_model(ModelType.LANGUAGE_SAFETY)
    assert docta_client.get_model() == ModelType.LANGUAGE_SAFETY

def test_run_docta_success(docta_client):
    docta_client.set_model(ModelType.LANGUAGE_SAFETY)
    with requests_mock.Mocker() as m:
        m.post('https://staging.api.docta.ai/api-key-language-safety', json={"response": json.dumps({'result': 'success'})}, status_code=200)
        response = docta_client.run_docta({'key': 'value'})
        assert response == {'result': 'success'}

def test_run_docta_no_model(docta_client):
    with pytest.raises(ValueError, match="model is not set"):
        docta_client.run_docta({'key': 'value'})

def test_run_docta_failed(docta_client):
    docta_client.set_model(ModelType.LANGUAGE_SAFETY)
    with requests_mock.Mocker() as m:
        m.post('https://staging.api.docta.ai/api-key-language-safety', json={'error': 'bad request'}, status_code=400)
        with pytest.raises(Exception):  # Adjust this to the specific exception you expect
            docta_client.run_docta({'key': 'value'})
