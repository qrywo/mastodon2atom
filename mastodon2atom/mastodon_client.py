from mastodon import Mastodon, MastodonUnauthorizedError, MastodonIllegalArgumentError
from mastodon.return_types import Account, InstanceV2, Status
from mastodon.types_base import PaginatableList
from mastodon2atom.credentials import Credentials
from mastodon2atom.settings import Settings


class MastodonClient:

    def __init__(self, credentials : Credentials, settings : Settings):
        self.credentials = credentials
        self.settings = settings
        self.app_scopes = ["read:statuses", "read:accounts"]

        api_base_url = self.settings.mastodon_instance_url
        client_id = self.credentials.mastodon_client_id
        client_secret = self.credentials.mastodon_client_secret
        access_token = self.credentials.mastodon_access_token
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
        client_id = self.credentials.mastodon_client_id
        client_secret = self.credentials.mastodon_client_secret

        if client_id is None or client_secret is None:
            app_name = self.settings.app_name
            client_id, client_secret = self.mastodon.create_app(client_name=app_name,
                                                                scopes=self.app_scopes,
                                                                api_base_url=api_base_url,
                                                                redirect_uris=oauth_redirect_url)
            self.credentials.mastodon_client_id = client_id
            self.credentials.mastodon_client_secret = client_secret

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
            self.credentials.mastodon_access_token = access_token
            return True
        except MastodonIllegalArgumentError:
            return False

    def get_home_timeline(self) -> PaginatableList[Status]:
        return self.mastodon.timeline_home()

    def get_instance(self) -> InstanceV2:
        return self.mastodon.instance_v2()

    def get_user(self) -> Account:
        return self.mastodon.me()