import os
from mastodon import Mastodon, MastodonUnauthorizedError, MastodonIllegalArgumentError
from dotenv import load_dotenv, set_key

class MastodonClient:

    def __init__(self):
        self.APP_NAME = "mastofeed"
        self.APP_SCOPES = ["read:statuses", "read:accounts"]

        self.ENV_FILE_PATH = "./.data/.env"
        load_dotenv(self.ENV_FILE_PATH)

        if "MASTODON_INSTANCE_DOMAIN" not in os.environ:
            os.environ["MASTODON_INSTANCE_DOMAIN"] = "mastodon.social"
        self.INSTANCE_URL = f"https://{os.getenv('MASTODON_INSTANCE_DOMAIN')}"

        client_id = os.getenv("MASTODON_CLIENT_ID")
        client_secret = os.getenv("MASTODON_CLIENT_SECRET")
        access_token = os.getenv("MASTODON_ACCESS_TOKEN")
        self.mastodon = Mastodon(api_base_url=self.INSTANCE_URL,
                                 access_token=access_token,
                                 client_id=client_id,
                                 client_secret=client_secret)

    def is_access_provided(self):
        try:
            self.mastodon.app_verify_credentials()
            return True
        except MastodonUnauthorizedError:
            return False

    def get_access_redirect_url(self, oauth_redirect_url):
        client_id = os.getenv("MASTODON_CLIENT_ID")
        client_secret = os.getenv("MASTODON_CLIENT_SECRET")
        if client_id is None or client_secret is None:
            client_id, client_secret = self.mastodon.create_app(client_name=self.APP_NAME,
                                                                scopes=self.APP_SCOPES,
                                                                api_base_url=self.INSTANCE_URL,
                                                                redirect_uris=oauth_redirect_url)
            set_key(self.ENV_FILE_PATH, "MASTODON_CLIENT_ID", client_id)
            set_key(self.ENV_FILE_PATH, "MASTODON_CLIENT_SECRET", client_secret)
        self.mastodon = Mastodon(api_base_url=self.INSTANCE_URL,
                                 client_id=client_id,
                                 client_secret=client_secret)
        return self.mastodon.auth_request_url(scopes=self.APP_SCOPES,
                                              redirect_uris=oauth_redirect_url)

    def grant_access(self, code, oauth_redirect_url):
        try:
            access_token = self.mastodon.log_in(code=code,
                                                scopes=self.APP_SCOPES,
                                                redirect_uri=oauth_redirect_url)
            set_key(self.ENV_FILE_PATH, "MASTODON_ACCESS_TOKEN", access_token)
            return True
        except MastodonIllegalArgumentError:
            return False

    def get_home_timeline(self):
        return self.mastodon.timeline_home()

    def get_home_timeline_url(self):
        return self.INSTANCE_URL + "/home"

    def get_instance_icon(self):
        return self.mastodon.instance_v2().icon[-1].src

    def get_instance_language(self):
        return self.mastodon.instance_v2().languages[0]

    def get_instance_logo(self):
        return self.mastodon.instance_v2().thumbnail.url

    @staticmethod
    def get_instance_domain():
        return os.getenv("MASTODON_INSTANCE_DOMAIN")

    def get_user(self):
        return self.mastodon.me()