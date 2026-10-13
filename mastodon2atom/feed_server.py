from flask import Flask, redirect, url_for, request, Response, abort, render_template, session
from flask_httpauth import HTTPBasicAuth
import logging
from mastodon2atom.access_mode import AccessMode
from mastodon2atom.credentials import Credentials
from mastodon2atom.feed_builder import FeedBuilder
from mastodon2atom.mastodon_client import MastodonClient
from mastodon2atom.settings import Settings
import secrets
from werkzeug.middleware.proxy_fix import ProxyFix


settings = Settings.load()
credentials = Credentials(settings.credentials_file_path)

app = Flask(settings.app_name)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.secret_key = secrets.token_hex(32)

authentication = HTTPBasicAuth()
mastodon_client = MastodonClient(credentials, settings)
feed_builder = FeedBuilder(mastodon_client, settings)

LOG_FORMAT = "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"
logging.basicConfig(format=LOG_FORMAT, datefmt=DATE_FORMAT, level="INFO")


@authentication.verify_password
def verify_app_password(username : str, password : str) -> bool:
    username_ok = secrets.compare_digest(username, settings.app_username)
    password_ok = secrets.compare_digest(password, settings.app_password)
    if (not username_ok or not password_ok) and username and password:
        logging.warning(f"{request.remote_addr} tried to log into the app "
                        f"with the username {username}, but failed.")
    if username_ok and password_ok:
        logging.info(f"{request.remote_addr} logged into the app successfully "
                     f"with the username {username}.")
    return username_ok and password_ok


@app.get("/")
@authentication.login_required
def home():
    result, error_name = mastodon_client.is_access_provided()

    if result is AccessMode.UNAUTHORIZED:
        session["state"] = secrets.token_hex(16)
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True),
                                                                session["state"]))
    if result is AccessMode.UNAVAILABLE:
        logging.error(result.value + error_name)
        abort(503)

    feed_token = credentials.app_feed_token
    app_name = settings.app_name
    return render_template("index.html",
                           icon_url=settings.app_icon_url,
                           feed_url=url_for("feed", _external=True, token=feed_token),
                           app_name=app_name)


@app.get("/oauth/callback")
@authentication.login_required
def oauth_callback():
    state = request.args.get("state")
    if state != session["state"]:
        logging.error(f"{request.remote_addr} tried to access the oauth callback with an invalid state.")
        abort(400)
    session.pop("state")

    error = request.args.get("error")
    error_description = request.args.get("error_description")
    if error:
        logging.error(error_description)
        abort(400)

    code = request.args.get("code") or ""
    result, error_name = mastodon_client.grant_access(code, url_for("oauth_callback", _external=True))
    if result is AccessMode.UNAUTHORIZED:
        logging.error(result.value)
        abort(400)
    if result is AccessMode.UNAVAILABLE:
        logging.error(result.value + error_name)
        abort(503)

    credentials.app_feed_token = secrets.token_urlsafe(32)
    logging.info("The app feed token was regenerated.")
    return redirect(url_for("home"))


@app.get("/feed")
@app.get("/feed/<token>")
def feed(token=None):
    provided_feed_token = token or request.args.get("token") or ""
    correct_feed_token = credentials.app_feed_token or ""
    feed_token_ok = secrets.compare_digest(provided_feed_token, correct_feed_token)

    if not provided_feed_token or not feed_token_ok:
        logging.info(f"{request.remote_addr} tried to use the following invalid feed token: {provided_feed_token}")
        abort(404)

    result, error_name = mastodon_client.is_access_provided()
    if result is AccessMode.UNAUTHORIZED:
        logging.error(result.value)
        abort(503)
    if result is AccessMode.UNAVAILABLE:
        logging.error(result.value + error_name)
        abort(503)

    logging.info(f"{request.remote_addr} accessed the feed successfully.")
    return Response(feed_builder.build_feed(url_for("feed", _external=True, token=correct_feed_token)),
                    mimetype="application/atom+xml")


@app.get("/favicon.ico")
def favicon():
    return redirect(settings.app_icon_url)


try:
    settings.validate()
except ValueError as e:
    error_message = str(e)
    @app.before_request
    def invalid_app_password():
        logging.error(error_message)
        abort(503)


if __name__ == "__main__":
    app.run()