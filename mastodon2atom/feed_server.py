from flask import Flask, redirect, url_for, request, Response, abort
import hmac
from mastodon2atom.mastodon_client import MastodonClient
from mastodon2atom.feed_builder import FeedBuilder
import os

app = Flask("mastodon2atom")
mastodon_client = MastodonClient()
feed_builder = FeedBuilder(mastodon_client)


@app.route("/")
def home():
    if not mastodon_client.is_access_provided():
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True)))
    icon_url = mastodon_client.get_instance_icon()
    page = ('<!DOCTYPE html>'
            '<html>'
            '<head>'
            f'<link rel="icon" href="{icon_url}"/>'
            f'<link rel="apple-touch-icon" href="{icon_url}"/>'
            '</head>'
            '<body>'
            '<h1>Your mastodon2atom server is successfully running!</h1>'
            f'<p>Use <a href="{url_for("feed")}">this link</a> to access your Mastodon home timeline as an ATOM feed.</p>'
            '</body>'
            '</html>')
    return Response(page)


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not mastodon_client.grant_access(code, url_for("oauth_callback", _external=True)):
        return Response(response="Please authorize mastodon2atom to access your Mastodon home timeline.",
                        status=401)
    return redirect(url_for("home"))

@app.route("/feed")
def feed():
    if not mastodon_client.is_access_provided():
        abort(401)
    return Response(feed_builder.build_feed(url_for("feed", _external=True)),
                    mimetype="application/xml")


@app.before_request
def check_authorization():
    authorization = request.authorization
    if authorization is None or authorization.username is None or authorization.password is None:
        return ask_for_authorization()

    username_ok = hmac.compare_digest(authorization.username, "mastodon2atom")
    password = os.getenv("APP_PASSWORD")
    assert password
    password_ok = hmac.compare_digest(authorization.password, password)
    if not username_ok or not password_ok:
        return ask_for_authorization()
    return None


def ask_for_authorization():
    return Response(response="Please log in to mastodon2atom to continue.",
                    status=401,
                    headers={"WWW-Authenticate" : 'Basic realm="mastodon2atom"'})


def is_app_password_valid():
    password = os.getenv("APP_PASSWORD")
    black_list = ['"', "'", "@", ":", "/", "\\", " ", "password", "mastodon", "atom", "mastodon2atom", "feed", "12345678"]
    if not password or len(password) < 8:
        return "The app password is either not specified or too short!"
    for black_string in black_list:
        if black_string in password:
            return f"The password contains the following invalid string: {black_string}"
    return None


app_password_invalid_response = is_app_password_valid()
if app_password_invalid_response:
    @app.before_request
    def invalid_app_password():
        return Response(response=app_password_invalid_response,
                        status=503)


if __name__ == "__main__":
    app.run()