from mastodon import Mastodon, MastodonUnauthorizedError, MastodonIllegalArgumentError


class MastodonClient:

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.APP_SCOPES = ["read:statuses", "read:accounts"]


        api_base_url = self.config_manager.get_mastodon_instance_url()
        client_id, client_secret = self.config_manager.get_mastodon_client_details()
        access_token = self.config_manager.get_mastodon_access_token()
        self.mastodon = Mastodon(api_base_url=api_base_url,
                                 client_id=client_id,
                                 client_secret=client_secret,
                                 access_token=access_token)

    def is_access_provided(self):
        try:
            self.mastodon.app_verify_credentials()
            return True
        except MastodonUnauthorizedError:
            return False

    def get_access_redirect_url(self, oauth_redirect_url):
        api_base_url = self.config_manager.get_mastodon_instance_url()
        client_id, client_secret = self.config_manager.get_mastodon_client_details()

        if client_id is None or client_secret is None:
            app_name = self.config_manager.get_app_name()
            client_id, client_secret = self.mastodon.create_app(client_name=app_name,
                                                                scopes=self.APP_SCOPES,
                                                                api_base_url=api_base_url,
                                                                redirect_uris=oauth_redirect_url)
            self.config_manager.set_mastodon_client_details(client_id, client_secret)

        self.mastodon = Mastodon(api_base_url=api_base_url,
                                 client_id=client_id,
                                 client_secret=client_secret)
        return self.mastodon.auth_request_url(scopes=self.APP_SCOPES,
                                              redirect_uris=oauth_redirect_url)

    def grant_access(self, code, oauth_redirect_url):
        try:
            access_token = self.mastodon.log_in(code=code,
                                                scopes=self.APP_SCOPES,
                                                redirect_uri=oauth_redirect_url)
            self.config_manager.set_mastodon_access_token(access_token)
            return True
        except MastodonIllegalArgumentError:
            return False

    def get_home_timeline(self):
        return self.mastodon.timeline_home()

    def get_home_timeline_url(self):
        return self.config_manager.get_mastodon_instance_home_url()

    def get_instance_icon(self):
        return self.mastodon.instance_v2().icon[-1].src

    def get_instance_language(self):
        return self.mastodon.instance_v2().languages[0]

    def get_instance_logo(self):
        return self.mastodon.instance_v2().thumbnail.url

    def get_user(self):
        return self.mastodon.me()