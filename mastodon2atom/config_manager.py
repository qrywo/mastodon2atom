from dotenv import load_dotenv, set_key
import os

class ConfigManager:

    def __init__(self, env_file_path="./.data/.env"):
        self.ENV_FILE_PATH = env_file_path
        load_dotenv(env_file_path)

        self.__app_feed_token = os.getenv("APP_FEED_TOKEN")

        self.__app_icon_url = os.getenv("APP_ICON_URL") or "https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg"

        self.__app_name = os.getenv("APP_NAME") or "mastodon2atom"

        self.__app_password = os.getenv("APP_PASSWORD")

        self.__app_username = os.getenv("APP_USERNAME") or "mastodon2atom"

        self.__mastodon_client_id = os.getenv("MASTODON_CLIENT_ID")
        self.__mastodon_client_secret = os.getenv("MASTODON_CLIENT_SECRET")
        self.__mastodon_access_token = os.getenv("MASTODON_ACCESS_TOKEN")

        self.__mastodon_instance_domain = os.getenv("MASTODON_INSTANCE_DOMAIN") or "mastodon.social"

    def get_app_feed_token(self):
        return self.__app_feed_token

    def get_app_icon_url(self):
        return self.__app_icon_url

    def get_app_name(self):
        return self.__app_name

    def get_app_password(self):
        black_list = ['"', "'", "@", ":", "/", "\\", " ",
                      "password", "mastodon", "atom", "mastodon2atom", "feed", "12345678"]
        if not self.__app_password:
            raise ValueError("The mandatory app password is not specified as an environment variable!")
        if len(self.__app_password) < 8:
            raise ValueError("The app password is too short (less than 8 characters)!")
        for black_string in black_list:
            if black_string in self.__app_password:
                raise ValueError(f"The password contains the following invalid string: {black_string}")
        return self.__app_password

    def get_app_username(self):
        return self.__app_username

    def get_mastodon_client_details(self):
        return self.__mastodon_client_id, self.__mastodon_client_secret

    def get_mastodon_access_token(self):
        return self.__mastodon_access_token

    def get_mastodon_instance_domain(self):
        return self.__mastodon_instance_domain

    def get_mastodon_instance_url(self):
        return f"https://{self.__mastodon_instance_domain}"

    def get_mastodon_instance_home_url(self):
        return f"https://{self.__mastodon_instance_domain}/home"

    def set_app_feed_token(self, feed_token):
        self.__app_feed_token = feed_token
        set_key(dotenv_path=self.ENV_FILE_PATH,
                key_to_set="APP_FEED_TOKEN",
                value_to_set=feed_token)

    def set_mastodon_client_details(self, client_id, client_secret):
        self.__mastodon_client_id = client_id
        set_key(dotenv_path=self.ENV_FILE_PATH,
                key_to_set="MASTODON_CLIENT_ID",
                value_to_set=client_id)
        self.__mastodon_client_secret = client_secret
        set_key(dotenv_path=self.ENV_FILE_PATH,
                key_to_set="MASTODON_CLIENT_SECRET",
                value_to_set=client_secret)

    def set_mastodon_access_token(self, access_token):
        self.__mastodon_access_token = access_token
        set_key(dotenv_path=self.ENV_FILE_PATH,
                key_to_set="MASTODON_ACCESS_TOKEN",
                value_to_set=access_token)