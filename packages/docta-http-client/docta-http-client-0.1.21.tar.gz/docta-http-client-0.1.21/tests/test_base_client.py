import pytest
import requests_mock
from src.docta_http_client.base_client import APIClient
from src.docta_http_client.utils import parse_json_response, check_status_code

@pytest.fixture
def api_client():
    return APIClient(api_key='fake_api_key', user_id='fake_user_id')

def test_get_successful(api_client):
    with requests_mock.Mocker() as m:
        m.get('https://staging.api.docta.ai/api-key-model_name', json={'success': True}, status_code=200)
        response = api_client.get('model_name', params={'key': 'value'})
        assert response == {'success': True}

def test_post_successful(api_client):
    with requests_mock.Mocker() as m:
        m.post('https://staging.api.docta.ai/api-key-model_name', json={'posted': True}, status_code=200)
        response = api_client.post('model_name', data={'key': 'value'})
        assert response == {'posted': True}

def test_get_failed(api_client):
    with requests_mock.Mocker() as m:
        m.get('https://staging.api.docta.ai/api-key-model_name', json={'error': 'not found'}, status_code=404)
        with pytest.raises(Exception):  # Adjust this to the specific exception you expect
            api_client.get('model_name', params={'key': 'value'})

def test_post_failed(api_client):
    with requests_mock.Mocker() as m:
        m.post('https://staging.api.docta.ai/api-key-model_name', json={'error': 'bad request'}, status_code=400)
        with pytest.raises(Exception):  # Adjust this to the specific exception you expect
            api_client.post('model_name', data={'key': 'value'})
