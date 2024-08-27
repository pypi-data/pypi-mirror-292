import json
import logging
import threading

import requests
from tqdm import tqdm


def parse_json_response(response):
    """
    Parses JSON response and checks for errors in response.
    """
    try:
        data = response.json()
        if 'error' in data:
            logging.error(f"Error from API: {data['error']}")
            raise Exception(f"API Error: {data['error']}")
        elif "success" in data:
            parsed_response = ''
            result = data.get("result")
            if result:
                result_data = json.loads(result)
                for key, value in result_data.items():
                    for topic, quality in value.items():
                        parsed_response += f"{topic}: {quality}\n"
            return parsed_response
        return data
    except ValueError:
        raise ValueError("Invalid JSON received")


def check_status_code(response):
    """
    Check if the HTTP status code indicates an error and raise an exception if so.
    """
    if response.status_code != 200:
        logging.error(f"HTTP Error {response.status_code}: {response.text}")
        response.raise_for_status()


stop_event = threading.Event()


def receive_sse(uri, headers):
    try:
        response = requests.get(uri, stream=True, headers=headers)
        buffer = ""
        progress_bar = tqdm(total=100, desc="Processing", unit="%")

        for chunk in response.iter_content(decode_unicode=True):
            if stop_event.is_set():
                break
            buffer += chunk
            while "\n\n" in buffer:
                line, buffer = buffer.split("\n\n", 1)
                for entry in line.split("\n"):
                    if entry.startswith("data:"):
                        data = entry[len("data:"):].strip()
                        if data:
                            try:
                                progress = int(data)
                                progress_bar.n = progress
                                progress_bar.last_print_n = progress
                                progress_bar.update(0)
                                if progress >= 100:
                                    progress_bar.close()
                                    print("Processing complete!")
                                    return
                            except ValueError:
                                print(f"Error parsing data as integer: {data}")
    except Exception as e:
        print(f"Error receiving SSE: {e}")


def start_sse_listener(self, file_identifier):
    hermes_url = 'https://api.docta.ai'
    sse_url = hermes_url + f"/sse/stream?file_identifier={file_identifier}"
    headers = {
        'apiKey': self.api_key,
        'userId': self.user_id
    }
    stop_event.clear()
    sse_thread = threading.Thread(target=lambda: receive_sse(sse_url, headers))
    sse_thread.start()
    return sse_thread
