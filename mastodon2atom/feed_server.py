from flask import Flask, redirect, url_for, request, Response, abort, render_template
from flask_httpauth import HTTPBasicAuth
import logging
from mastodon2atom.credentials import Credentials
from mastodon2atom.feed_builder import FeedBuilder
from mastodon2atom.mastodon_client import MastodonClient
from mastodon2atom.settings import Settings
from pathlib import Path
import secrets


credentials = Credentials(Path("./.data/credentials.json"))
settings = Settings.load()

app = Flask(settings.app_name)
authentication = HTTPBasicAuth()
mastodon_client = MastodonClient(credentials, settings)
feed_builder = FeedBuilder(mastodon_client, settings)

LOG_FORMAT = "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"
logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT, level="INFO")


@authentication.verify_password
def verify_app_password(username, password):
    username_ok = secrets.compare_digest(username, settings.app_username)
    password_ok = secrets.compare_digest(password, settings.app_password)
    if (not username_ok or not password_ok) and username and password:
        logging.warning(f"{request.remote_addr} tried to log into the app "
                        f"with the username {username} and the password {password}, but failed.")
    return username_ok and password_ok


@app.errorhandler(404)
def feed_not_found(_):
    return (render_template("not_found.html",
                           icon_url=settings.app_icon_url),
            404)

@app.errorhandler(503)
def bad_app_password(_):
    return (render_template("service_unavailable.html",
                           icon_url=settings.app_icon_url),
            503)

@app.get("/")
@authentication.login_required
def home():
    if not mastodon_client.is_access_provided():
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True)))
    feed_token = credentials.get("APP_FEED_TOKEN")
    app_name = settings.app_name
    return render_template("index.html",
                           icon_url=settings.app_icon_url,
                           feed_url=url_for("feed", _external=True, token=feed_token),
                           app_name=app_name)


@app.get("/oauth/callback")
@authentication.login_required
def oauth_callback():
    code = request.args.get("code")
    if not mastodon_client.grant_access(code, url_for("oauth_callback", _external=True)):
        app_name = settings.app_name
        logging.error(f"Please authorize {app_name} to access your Mastodon home timeline.")
        abort(503)
    feed_token = secrets.token_urlsafe(32)
    credentials.set("APP_FEED_TOKEN", feed_token)
    return redirect(url_for("home"))


@app.get("/feed")
@app.get("/feed/<token>")
def feed(token=None):
    feed_token = token or request.args.get("token")
    if not feed_token:
        logging.error(f"{request.remote_addr} tried to access the feed, but did not provide a feed token.")
        abort(404)
    feed_token_ok = secrets.compare_digest(feed_token, credentials.get("APP_FEED_TOKEN"))
    if not feed_token_ok:
        logging.info(f"{request.remote_addr} tried to use the following invalid feed token: {feed_token}")
        abort(404)
    if not mastodon_client.is_access_provided():
        app_name = settings.app_name
        logging.error(f"The access token for {app_name} seems to be invalid. "
                      "Please delete the credentials.json file in the .data folder "
                      "and restart the application.")
        abort(503)
    logging.info(f"{request.remote_addr} accessed the feed successfully.")
    return Response(feed_builder.build_feed(url_for("feed", _external=True, token=feed_token)),
                    mimetype="application/xml")


@app.get("/favicon.ico")
def favicon():
    return redirect(settings.app_icon_url)


try:
    settings.validate_app_password()
except ValueError as e:
    error_message = str(e)
    @app.before_request
    def invalid_app_password():
        logging.error(error_message)
        abort(503)


if __name__ == "__main__":
    app.run()