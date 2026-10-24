# mastodon2atom

mastodon2atom lets you run an ATOM feed server to access your personal home timeline on Mastodon as an ATOM feed.

Mastodon offers RSS feeds for the toots of a specific user (e.g., [https://mastodon.social/@Mastodon.rss](https://mastodon.social/@Mastodon.rss)). However, there is currently (as of October 2026) no option to access the personal home timeline on Mastodon as an RSS/ATOM feed ([here](https://github.com/mastodon/mastodon/issues/18601) is the open GitHub issue). That's why I built this tool.

# Setup

## Prerequisites

If you want to run the ATOM feed server on a remote server, please configure a proper HTTPS capable reverse proxy (e.g., with nginx + certbot, or with caddy) and point the reverse proxy to the local IP address [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Running the Application

You can run the Docker container with one of the two following options.

### A) Quick Start

Run the Docker container with the following command. Replace `[YOUR_APP_PASSWORD]` with a secure password, obviously.

```shell
docker run -d -v .mastodon2atom_data:/app/.mastodon2atom_data -p 127.0.0.1:8000:8000 --restart unless-stopped -e APP_PASSWORD=[YOUR_APP_PASSWORD] ghcr.io/qrywo/mastodon2atom
```

Alternatively, you can pull the Docker image from Docker Hub instead of GitHub Container Registry (with `qrywo/mastodon2atom` instead of `ghcr.io/qrywo/mastodon2atom`).

### B) Building the Image Yourself

Clone the project and change the directory to the repository.

```shell
git clone https://github.com/qrywo/mastodon2atom.git
cd mastodon2atom
```

Build the Docker container.

```shell
docker build -t mastodon2atom .
```

Run the Docker container with the following command. Replace `[YOUR_APP_PASSWORD]` with a secure password, obviously. You can adjust the options if necessary.

```shell
docker run -d -v .mastodon2atom_data:/app/.mastodon2atom_data -p 127.0.0.1:8000:8000 --restart unless-stopped -e APP_PASSWORD=[YOUR_APP_PASSWORD] mastodon2atom
```

It is not necessary to mount the `.mastodon2atom_data` folder into the Docker container. However, the `.mastodon2atom_data` folder contains the Mastodon access token and the app feed token. So if you do not want to authorize mastodon2atom and copy the new app feed token into your feed reader after every restart of the Docker container, this is highly recommended.

## Using the Application

Now type the IP address or domain of your server into the web browser and follow the instructions of the configuration process. You will have to log in (first, with your app username and your app password, and second, into your Mastodon account) and authorize the application to access your Mastodon home timeline. If everything went well, you will receive a link to access the ATOM feed. If an error occurs, please check the logs of the Docker container for further information.

# Environment Variables

You can configure various environment variables when running the Docker container.

## Mandatory Environment Variables

- `APP_PASSWORD`: This is the password you need to access the application for the configuration process. Please specify a secure password (otherwise, the server will reject every request).

## Optional Environment Variables

- `APP_ICON_URL`: This is the icon used in the web browser or in the feed reader. Defaults to [this URL](https://upload.wikimedia.org/wikipedia/commons/4/43/Feed-icon.svg).
- `APP_USERNAME`: This is the username you need to access the application for the configuration process. Defaults to *mastodon2atom*.
- `MASTODON_INSTANCE_DOMAIN`: This is the domain of your Mastodon instance. Defaults to *mastodon.social*.

# Disclaimer

This software is not affiliated with or endorsed by Mastodon GmbH or Mastodon Inc.