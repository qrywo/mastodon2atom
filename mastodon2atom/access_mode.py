from enum import Enum

class AccessMode(Enum):
    OK = "ok"
    UNAUTHORIZED = ("The app is not authorized to access your Mastodon home timeline: ",
                    "Either you did not create an access token yet by authorizing the app ",
                    "or the access token is invalid (wrong or revoked).")
    UNAVAILABLE = "Your specified Mastodon instance is currently not available due to the following error: "