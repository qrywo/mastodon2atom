# mastodon2atom

mastodon2atom lets you run an ATOM feed server to access your personal home timeline on Mastodon as an ATOM feed.

# Setup

If you want to run the ATOM feed server on a remote server, please configure a proper HTTPS capable reverse proxy (e.g., with nginx + certbot or caddy) and point the reverse proxy to the local IP address [http://127.0.0.1:8000](http://127.0.0.1:8000).

Clone the project and change the directory to the repository.

```shell
git clone https://github.com/qrywo/mastodon2atom.git
cd mastodon2atom
```

Build the Docker container.

```shell
docker build -t mastodon2atom .
```

Run the Docker container with the following command (replace `[YOUR_APP_PASSWORD]` with a secure password obviously). You can adjust the options if necessary.

```shell
docker run -d -v .data:/app/.data -p 127.0.0.1:8000:8000 --restart unless-stopped -e APP_PASSWORD=[YOUR_APP_PASSWORD] mastodon2atom
```

Now type the IP address or domain of your server into the web browser and follow the instructions of the configuration process. You will have to log in (first, with your app username and your app password, and second, into your Mastodon account) and authorize the application to access your Mastodon home timeline. If everything went well, you will receive a link to access the ATOM feed. If an error occurs, please check the logs of the docker container for further information.

# Environment Variables

You can configure various environment variables before running the Docker container.

## Mandatory Environment Variables

- `APP_PASSWORD`: This is the password you need to access the application for the configuration process. Please specify a secure password (otherwise, the server will reject every request).

## Optional Environment Variables

- `APP_ICON_URL`: This is the icon used in the web browser or in the feed reader. Defaults to [this URL](https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg).
- `APP_USERNAME`: This is the username you need to access the application for the configuration process. Defaults to *mastodon2atom*.
- `MASTODON_INSTANCE_DOMAIN`: This is the domain of your Mastodon instance. Defaults to *mastodon.social*.

# Disclaimer

This software is not affiliated with or endorsed by Mastodon GmbH or Mastodon Inc.