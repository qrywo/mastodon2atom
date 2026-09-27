from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

class FeedBuilder:

    def __init__(self, mastodon_client):
        self.feed_generator = None
        self.mastodon_client = mastodon_client

    def build_feed(self, feed_url):
        self.__build_feed_generator(feed_url)

        for status in self.mastodon_client.get_home_timeline():
            self.__build_feed_entry(status)

        return self.feed_generator.atom_str(pretty=True)

    def __build_feed_generator(self, feed_url):
        self.feed_generator = FeedGenerator()

        self.feed_generator.title("\U0001F3E0 " + self.mastodon_client.get_user().username +
                                  "@" + self.mastodon_client.get_instance_domain())
        self.feed_generator.subtitle(f"\U0001F464: {self.mastodon_client.get_user().display_name} " +
                                     f"({self.mastodon_client.get_user().username});\t" +
                                     f"\U0001F310: {self.mastodon_client.get_instance_domain()}")
        self.feed_generator.id(feed_url)
        self.feed_generator.link(href=feed_url, rel="self", type="application/atom+xml")
        self.feed_generator.link(href=self.mastodon_client.get_home_timeline_url(), rel="alternate", type="text/html")
        self.feed_generator.logo(self.mastodon_client.get_instance_logo())
        self.feed_generator.updated(datetime.now(timezone.utc))
        self.feed_generator.icon(self.mastodon_client.get_instance_icon())
        self.feed_generator.generator(generator="python-feedgen",
                                      version="1.0.0",
                                      uri="https://lkiesow.github.io/python-feedgen")
        self.feed_generator.language(self.mastodon_client.get_instance_language())

        self.feed_generator.load_extension("media")

    def __build_feed_entry(self, status):
        feed_entry = self.feed_generator.add_entry()

        feed_entry.published(status.created_at)
        feed_entry.updated(status.edited_at)

        if status.reblog is not None:
            original_status = status.reblog
            feed_entry.title(f"\U0001F501 [{status.account.display_name}] \U00002192 " +
                             f"\U0001F4AC [{status.reblog.account.display_name}]")
        else:
            original_status = status
            feed_entry.title(f"\U0001F4AC [{status.account.display_name}]")

        feed_entry.id(original_status.url)
        feed_entry.link(href=original_status.url, rel="alternate")
        feed_entry.author(name=original_status.account.display_name,
                          uri=original_status.account.url)

        content = str(original_status.content)
        content = self.__emojify_content(content, original_status.emojis)

        soup = BeautifulSoup(content, "html.parser")
        summary = soup.get_text()

        for tag in original_status.tags:
            feed_entry.category(term=tag.name, label="#" + tag.name)

        self.__add_media_to_entry(feed_entry, original_status.media_attachments)
        content = self.__add_media_to_content(content, original_status.media_attachments)

        feed_entry.summary(summary=summary, type="text")
        feed_entry.content(content=content, type="html")

    @staticmethod
    def __emojify_content(content, emojis):
        for emoji in emojis:
            emoji_text = f":{emoji.shortcode}:"
            emoji_repr = ('<img rel="emoji" '
                          'draggable="false" '
                          'width="16" '
                          'height="16" '
                          'class="emojione" '
                          'style="height: 1.1em; margin: -.2ex .15em .2ex; object-fit: contain; vertical-align: middle; width: 1.1em;" '
                          f'alt=":{emoji.shortcode}:" '
                          f'title=":{emoji.shortcode}:" '
                          f'src="{emoji.static_url}"/>')
            content = content.replace(emoji_text, emoji_repr)
        return content

    @staticmethod
    def __add_media_to_entry(feed_entry, media_attachments):
        for attachment in media_attachments:
            content_url = attachment.url
            medium = attachment.type
            content_width = None
            content_height = None
            frame_rate = None
            duration = None
            bit_rate = None
            if attachment.type in ["video", "gifv"]:
                medium = "video"
                content_width = str(attachment.meta.original.width)
                content_height = str(attachment.meta.original.height)
                frame_rate = str(attachment.meta.original.frame_rate)
                duration = str(attachment.meta.original.duration)

                # calculate bytes per second (mastodon) to kilobits per second (feedgen)
                bit_rate = str(round(attachment.meta.original.bitrate * 0.008))
            elif attachment.type == "image":
                content_width = str(attachment.meta.original.width)
                content_height = str(attachment.meta.original.height)
            elif attachment.type == "audio":
                duration = str(attachment.meta.original.duration)

                # calculate bytes per second (mastodon) to kilobits per second (feedgen)
                bit_rate = str(round(attachment.meta.original.bitrate * 0.008))
            else:
                medium = None
            thumbnail_url = attachment.preview_url
            thumbnail_width = str(attachment.meta.small.width)
            thumbnail_height = str(attachment.meta.small.height)

            feed_entry.media.content(url=content_url, medium=medium, width=content_width, height=content_height,
                                     framerate=frame_rate, duration=duration, bitrate=bit_rate)
            feed_entry.media.thumbnail(url=thumbnail_url, width=thumbnail_width, height=thumbnail_height)

    @staticmethod
    def __add_media_to_content(content, media_attachments):
        for attachment in media_attachments:
            attachment_string : str
            url = attachment.url
            alt = attachment.description
            if attachment.type == "image":
                attachment_string = (f'<p><a href="{url}">'
                                     f'<img src="{url}" alt="{alt}"/>'
                                     '</a></p>')
            elif attachment.type in ["video", "gifv"]:
                preview_url = attachment.preview_url
                attachment_string = (f'<p><a href="{url}">'
                                     f'<p><img src="{preview_url}" alt="{alt}"/></p>'
                                     f'\U000021B3 \U0001F3A5: {alt} \U00002197'
                                     '</a></p>')
            elif attachment.type == "audio":
                attachment_string = (f'<p><a href="{url}">'
                                     f'\U0001F3A7: {alt} \U00002197'
                                     '</a></p>')
            else:
                attachment_string = (f'<p><a href="{url}">'
                                     f'\U0001F4CE: {alt} \U00002197'
                                     '</a></p>')
            content += attachment_string
        return content