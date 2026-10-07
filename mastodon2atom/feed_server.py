from flask import Flask, redirect, url_for, request, Response, abort
from mastofeed.mastodon_client import MastodonClient
from mastofeed.feed_builder import FeedBuilder

app = Flask("mastodon2atom")
mastodon_client = MastodonClient()
feed_builder = FeedBuilder(mastodon_client)


@app.route("/")
def default():
    icon_url = mastodon_client.get_instance_icon()
    page = ('<!DOCTYPE html>'
            '<html>'
            '<head>'
            f'<link rel="icon" href="{icon_url}"/>'
            f'<link rel="apple-touch-icon" href="{icon_url}"/>'
            '</head>'
            '<body>'
            '<h1>Your mastodon2atom server is running!</h1>'
            f'<p>Use <a href="{url_for("login")}">this link</a> to log in and authorize mastodon2atom.</p>'
            f'<p>Use <a href="{url_for("feed")}">this link</a> to access the home timeline as an ATOM feed.</p>'
            '</body>'
            '</html>')
    return Response(page)

@app.route("/login")
def login():
    if not mastodon_client.is_access_provided():
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True)))
    return redirect(url_for("feed"))


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not mastodon_client.grant_access(code, url_for("oauth_callback", _external=True)):
        abort(401)
    return redirect(url_for("feed"))

@app.route("/feed")
def feed():
    if not mastodon_client.is_access_provided():
        abort(401)
    return Response(feed_builder.build_feed(url_for("feed", _external=True)),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run()