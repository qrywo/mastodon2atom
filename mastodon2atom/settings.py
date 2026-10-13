from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Self

@dataclass(frozen=True)
class Settings:

    app_icon_url : str
    app_name : str
    app_password : str
    app_username : str
    credentials_file_path : Path
    mastodon_instance_domain : str

    @property
    def mastodon_instance_url(self) -> str:
        return f"https://{self.mastodon_instance_domain}"

    @property
    def mastodon_instance_home_url(self) -> str:
        return f"https://{self.mastodon_instance_domain}/home"

    @classmethod
    def load(cls) -> Self:
        settings = cls(
            app_icon_url=os.getenv("APP_ICON_URL",
                                   "https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg"),
            app_name=os.getenv("APP_NAME", "mastodon2atom"),
            app_password=os.getenv("APP_PASSWORD", ""),
            app_username=os.getenv("APP_USERNAME", "mastodon2atom"),
            credentials_file_path=Path(os.getenv("CREDENTIALS_FILE_PATH", "./.data/credentials.json")),
            mastodon_instance_domain=os.getenv("MASTODON_INSTANCE_DOMAIN", "mastodon.social")
        )
        return settings

    def validate(self):
        regex = "[!()*+,.0-9;<=>A-Z_a-z{|}~-]+"
        compiled_regex = re.compile(regex)
        black_list = ["password", "mastodon", "atom", "mastodon2atom", "feed", "12345678"]

        if not self.app_password:
            raise ValueError("The mandatory app password is not specified as an environment variable!")
        if len(self.app_password) < 8:
            raise ValueError("The app password is too short (less than 8 characters)!")
        for black_string in black_list:
            if black_string in self.app_password:
                raise ValueError(f"The app password contains the following invalid string: {black_string}")
        if compiled_regex.fullmatch(self.app_username) is None:
            raise ValueError(f"The app username does not match the following regex: {regex}")
        if compiled_regex.fullmatch(self.app_password) is None:
            raise ValueError(f"The app password does not match the following regex: {regex}")