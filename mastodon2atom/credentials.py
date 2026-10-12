import json

class Credentials:

    def __init__(self, credentials_file_path):
        self.credentials_file_path = credentials_file_path

    def get(self, key):
        if not self.credentials_file_path.exists():
            return None
        json_credentials = self.credentials_file_path.read_text()
        parsed_credentials = json.loads(json_credentials)
        return parsed_credentials

    def set(self, key, value):
        if not self.credentials_file_path.exists():
            parsed_credentials = {}
        else:
            json_credentials = self.credentials_file_path.read_text()
            parsed_credentials = json.loads(json_credentials)
        parsed_credentials[key] = value
        json_credentials = json.dumps(parsed_credentials)
        self.credentials_file_path.write_text(json_credentials)