from mastodon import Mastodon, MastodonUnauthorizedError, MastodonIllegalArgumentError
from mastodon.return_types import Status, Account
from mastodon.types_base import PaginatableList
from mastodon2atom.credentials import Credentials
from mastodon2atom.settings import Settings


class MastodonClient:

    def __init__(self, credentials : Credentials, settings : Settings):
        self.credentials = credentials
        self.settings = settings
        self.app_scopes = ["read:statuses", "read:accounts"]

        api_base_url = self.settings.mastodon_instance_url
        client_id = self.credentials.get("MASTODON_CLIENT_ID")
        client_secret = self.credentials.get("MASTODON_CLIENT_SECRET")
        access_token = self.credentials.get("MASTODON_ACCESS_TOKEN")
        self.mastodon = Mastodon(api_base_url=api_base_url,
                                 client_id=client_id,
                                 client_secret=client_secret,
                                 access_token=access_token)

    def is_access_provided(self) -> bool:
        try:
            self.mastodon.app_verify_credentials()
            return True
        except MastodonUnauthorizedError:
            return False

    def get_access_redirect_url(self, oauth_redirect_url : str) -> str:
        api_base_url = self.settings.mastodon_instance_url
        client_id = self.credentials.get("MASTODON_CLIENT_ID")
        client_secret = self.credentials.get("MASTODON_CLIENT_SECRET")

        if client_id is None or client_secret is None:
            app_name = self.settings.app_name
            client_id, client_secret = self.mastodon.create_app(client_name=app_name,
                                                                scopes=self.app_scopes,
                                                                api_base_url=api_base_url,
                                                                redirect_uris=oauth_redirect_url)
            self.credentials.set("MASTODON_CLIENT_ID", client_id)
            self.credentials.set("MASTODON_CLIENT_SECRET", client_secret)

        self.mastodon = Mastodon(api_base_url=api_base_url,
                                 client_id=client_id,
                                 client_secret=client_secret)
        return self.mastodon.auth_request_url(scopes=self.app_scopes,
                                              redirect_uris=oauth_redirect_url)

    def grant_access(self, code : str, oauth_redirect_url : str) -> bool:
        try:
            access_token = self.mastodon.log_in(code=code,
                                                scopes=self.app_scopes,
                                                redirect_uri=oauth_redirect_url)
            self.credentials.set("MASTODON_ACCESS_TOKEN", access_token)
            return True
        except MastodonIllegalArgumentError:
            return False

    def get_home_timeline(self) -> PaginatableList[Status]:
        return self.mastodon.timeline_home()

    def get_home_timeline_url(self) -> str:
        return self.settings.mastodon_instance_home_url

    def get_instance_icon_url(self) -> str:
        return self.mastodon.instance_v2().icon[-1].src

    def get_instance_language(self) -> str:
        return self.mastodon.instance_v2().languages[0]

    def get_instance_logo(self) -> str:
        return self.mastodon.instance_v2().thumbnail.url

    def get_user(self) -> Account:
        return self.mastodon.me()