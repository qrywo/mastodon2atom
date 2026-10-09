from flask import Flask, redirect, url_for, request, Response, abort
from flask_httpauth import HTTPBasicAuth
from mastodon2atom.config_manager import ConfigManager
from mastodon2atom.feed_builder import FeedBuilder
from mastodon2atom.mastodon_client import MastodonClient
import secrets


config_manager = ConfigManager()
app = Flask(config_manager.get_app_name())
authentication = HTTPBasicAuth()
mastodon_client = MastodonClient(config_manager)
feed_builder = FeedBuilder(mastodon_client, config_manager)


try:
    config_manager.get_app_password()
except ValueError as e:
    error_message = str(e)
    @app.before_request
    def invalid_app_password():
        return Response(response=error_message,
                        status=503)


@authentication.verify_password
def verify_app_password(username, password):
    username_ok = secrets.compare_digest(username, config_manager.get_app_username())
    password_ok = secrets.compare_digest(password, config_manager.get_app_password())
    return username_ok and password_ok


@app.route("/")
@authentication.login_required
def home():
    if not mastodon_client.is_access_provided():
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True)))
    icon_url = mastodon_client.get_instance_icon()
    feed_token = config_manager.get_app_feed_token()
    app_name = config_manager.get_app_name()
    page = ('<!DOCTYPE html>'
            '<html>'
            '<head>'
            f'<link rel="icon" href="{icon_url}"/>'
            f'<link rel="apple-touch-icon" href="{icon_url}"/>'
            '</head>'
            '<body>'
            f'<h1>Your {app_name} server is successfully running!</h1>'
            f'<p>Use <a href="{url_for("feed", _external=True, token=feed_token)}">this link</a> '
            'to access your Mastodon home timeline as an ATOM feed.</p>'
            '</body>'
            '</html>')
    return Response(page)


@app.route("/oauth/callback")
@authentication.login_required
def oauth_callback():
    code = request.args.get("code")
    if not mastodon_client.grant_access(code, url_for("oauth_callback", _external=True)):
        app_name = config_manager.get_app_name()
        return Response(response=f"Please authorize {app_name} to access your Mastodon home timeline.",
                        status=401)
    feed_token = secrets.token_urlsafe(32)
    config_manager.set_app_feed_token(feed_token)
    return redirect(url_for("home"))


@app.route("/feed")
def feed():
    feed_token = request.args.get("token")
    if not feed_token:
        abort(401)
    token_ok = secrets.compare_digest(feed_token, config_manager.get_app_feed_token())
    if not mastodon_client.is_access_provided() or not token_ok:
        abort(401)
    return Response(feed_builder.build_feed(url_for("feed", _external=True, token=feed_token)),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run()