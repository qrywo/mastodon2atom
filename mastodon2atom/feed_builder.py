from bs4 import BeautifulSoup
from datetime import datetime, timezone
from feedgen.entry import FeedEntry
from feedgen.feed import FeedGenerator
import html
from mastodon.return_types import Status, CustomEmoji, MediaAttachment
from mastodon.types_base import NonPaginatableList
from mastodon2atom.mastodon_client import MastodonClient
from mastodon2atom.settings import Settings

class FeedBuilder:

    def __init__(self, mastodon_client : MastodonClient, settings : Settings):
        self.mastodon_client = mastodon_client
        self.settings = settings

    def build_feed(self, feed_url : str) -> str:
        feed_generator = self._build_feed_generator(feed_url)

        for status in self.mastodon_client.get_home_timeline():
            self._build_feed_entry(feed_generator, status)

        return feed_generator.atom_str(pretty=True)

    def _build_feed_generator(self, feed_url : str) -> FeedGenerator:
        feed_generator = FeedGenerator()

        user = self.mastodon_client.get_user()
        feed_generator.title("\U0001F3E0 @" + user.username +
                             "@" + self.settings.mastodon_instance_domain)
        feed_generator.subtitle(f"\U0001F464: {user.display_name} " +
                                f"({user.username});\t" +
                                f"\U0001F310: {self.settings.mastodon_instance_domain}")

        feed_generator.id(feed_url)
        feed_generator.link(href=feed_url, rel="self", type="application/atom+xml")
        feed_generator.link(href=self.settings.mastodon_instance_home_url, rel="alternate", type="text/html")

        instance = self.mastodon_client.get_instance()
        feed_generator.logo(instance.thumbnail.url)
        feed_generator.updated(datetime.now(timezone.utc))
        feed_generator.icon(instance.icon[-1].src)
        feed_generator.generator(generator="python-feedgen",
                                      version="1.0.0",
                                      uri="https://lkiesow.github.io/python-feedgen")
        feed_generator.language(instance.languages[0])

        feed_generator.load_extension("media")
        return feed_generator

    def _build_feed_entry(self, feed_generator : FeedGenerator, status : Status):
        feed_entry = feed_generator.add_entry()

        feed_entry.published(status.created_at)
        feed_entry.updated(status.edited_at or status.created_at)

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
        content = self._emojify_content(content, original_status.emojis)

        soup = BeautifulSoup(content, "html.parser")
        summary = soup.get_text()

        for tag in original_status.tags:
            feed_entry.category(term=tag.name, label="#" + tag.name)

        self._add_media_to_entry(feed_entry, original_status.media_attachments)
        content = self._add_media_to_content(content, original_status.media_attachments)

        feed_entry.summary(summary=summary, type="text")
        feed_entry.content(content=content, type="html")

    @staticmethod
    def _emojify_content(content, emojis : NonPaginatableList[CustomEmoji]) -> str:
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
    def _add_media_to_entry(feed_entry : FeedEntry, media_attachments : NonPaginatableList[MediaAttachment]):
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
    def _add_media_to_content(content : str, media_attachments : NonPaginatableList[MediaAttachment]):
        for attachment in media_attachments:
            url = attachment.url
            alt = html.escape(attachment.description or "")
            if attachment.type == "image":
                attachment_string = (f'<p><a href="{url}">'
                                     f'<img src="{url}" alt="{alt}"/>'
                                     '</a></p>')
            elif attachment.type in ["video", "gifv"]:
                preview_url = attachment.preview_url
                attachment_string = (f'<p><a href="{url}">'
                                     f'<p><img src="{preview_url}" alt="{alt}"/></p>'
                                     f'\U000021B3 \U0001F3A5: {alt}'
                                     '</a></p>')
            elif attachment.type == "audio":
                attachment_string = (f'<p><a href="{url}">'
                                     f'\U0001F3A7: {alt}'
                                     '</a></p>')
            else:
                attachment_string = (f'<p><a href="{url}">'
                                     f'\U0001F4CE: {alt}'
                                     '</a></p>')
            content += attachment_string
        return content