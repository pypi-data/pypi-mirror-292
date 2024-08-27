from .base_client import APIClient
from .models import ModelType
from .utils import parse_json_response
import json
import requests


class DoctaHTTPClient(APIClient):
    def __init__(self, api_key, user_id):
        super().__init__(api_key, user_id)
        self.model = None

    def set_model(self, model: ModelType):
        self.model = model

    def get_model(self):
        return self.model

    def run_docta(self, data):
        if not self.model:
            raise ValueError("model is not set")
        return self.post(self.model._value_, data)

    def low_quality_detection(self, message: str):
        hermes_url = 'https://staging.api.docta.ai'
        client = requests.Session()
        headers = {
            'apiKey': self.api_key,
            'userId': self.user_id,
            'Content-Type': 'application/json'
        }
        data = {
            "message": message
        }
        response = client.post(hermes_url + '/api-key-low-quality-detection', headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"http post fail: {response.status_code}")
            return

        print(parse_json_response(response))
