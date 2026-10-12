import json
import os
from pathlib import Path

class Credentials:

    def __init__(self, credentials_file_path : Path):
        self.credentials_file_path = credentials_file_path
        self.credentials_file_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def app_feed_token(self) -> str | None:
        return self._get("APP_FEED_TOKEN")

    @app_feed_token.setter
    def app_feed_token(self, value : str):
        self._set("APP_FEED_TOKEN", value)

    @property
    def mastodon_access_token(self) -> str | None:
        return self._get("MASTODON_ACCESS_TOKEN")

    @mastodon_access_token.setter
    def mastodon_access_token(self, value : str):
        self._set("MASTODON_ACCESS_TOKEN", value)

    @property
    def mastodon_client_id(self) -> str | None:
        return self._get("MASTODON_CLIENT_ID")

    @mastodon_client_id.setter
    def mastodon_client_id(self, value : str):
        self._set("MASTODON_CLIENT_ID", value)

    @property
    def mastodon_client_secret(self) -> str | None:
        return self._get("MASTODON_CLIENT_SECRET")

    @mastodon_client_secret.setter
    def mastodon_client_secret(self, value : str):
        self._set("MASTODON_CLIENT_SECRET", value)

    def _get(self, key : str) -> str | None:
        if not self.credentials_file_path.exists():
            return None
        json_credentials = self.credentials_file_path.read_text()
        parsed_credentials = json.loads(json_credentials)
        return parsed_credentials.get(key)

    def _set(self, key : str, value : str):
        if not self.credentials_file_path.exists():
            parsed_credentials = {}
        else:
            json_credentials = self.credentials_file_path.read_text()
            parsed_credentials = json.loads(json_credentials)
        parsed_credentials[key] = value
        json_credentials = json.dumps(parsed_credentials)
        self.credentials_file_path.write_text(json_credentials)
        os.chmod(self.credentials_file_path, 0o600)