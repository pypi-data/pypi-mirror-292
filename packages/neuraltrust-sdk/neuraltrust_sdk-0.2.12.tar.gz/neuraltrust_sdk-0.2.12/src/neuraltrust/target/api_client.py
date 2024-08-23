import yaml
import json
import requests
from jsonpath_ng import parse
from datetime import datetime, timedelta
from sseclient import SSEClient

class APIClient:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)
        self.auth_token = None
        self.token_expiry = None

    def get_auth_token(self):
        if self.auth_token and datetime.now() < self.token_expiry:
            return self.auth_token

        try:
            response = requests.post(
                self.config['token_url'],
                json={
                    "user": self.config['username'],
                    "password": self.config['password']
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            self.auth_token = response.json()['token']
            # Set token expiry to 1 hour from now (adjust as needed)
            self.token_expiry = datetime.now() + timedelta(hours=1)
            return self.auth_token
        except requests.RequestException as e:
            print(f"Error getting auth token: {e}")
            return None

    def get_api_data(self):
        token = self.get_auth_token()
        if not token:
            return None

        try:
            headers = self.config.get('headers', {})
            headers['Authorization'] = f"Bearer {token}"
            print(self.config.get('payload'))
            
            response = requests.post(
                self.config['url'],
                json=self.config.get('payload'),
                headers=headers,
                stream=True
            )
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            last_json = None
            
            if 'text/event-stream' in content_type:
                # Handle EventStream
                client = SSEClient(response)
                for event in client.events():
                    if event.event == 'message':
                        try:
                            data = json.loads(event.data)
                            # Store the last JSON object
                            last_json = data
                            print(f"Received event: {data}")
                        except json.JSONDecodeError:
                            print(f"Received non-JSON event: {event.data}")
                # Extract the desired field from the last JSON object
                if last_json and 'response' in self.config:
                    field = self.config['response']
                    jsonpath_expr = parse(field)
                    matches = jsonpath_expr.find(last_json)
                    if matches:
                        return matches[0].value
                    else:
                        return None
                return last_json  # Return the last JSON object if no specific field is configured
            else:
                # Handle JSON response
                data = response.json()
                if 'response' in self.config:
                    field = self.config['response']
                    jsonpath_expr = parse(field)
                    matches = jsonpath_expr.find(data)
                    if matches:
                        return matches[0].value
                    else:
                        return None
                return data
        except requests.RequestException as e:
            import traceback
            traceback.print_exc()
            return None

# Usage
if __name__ == "__main__":
    client = APIClient('api_config.yaml')
    extracted_data = client.get_api_data()
    if extracted_data:
        print(extracted_data)
    else:
        print("Failed to obtain data")