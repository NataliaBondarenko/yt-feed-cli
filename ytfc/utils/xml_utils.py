from typing import List, Union, Dict

from lxml import etree, html

from ytfc.utils.decorators import lxml_exceptions
from ytfc.utils.settings import FEED_ITEMS


class XMLHandler:
    def __init__(self):
        self.feed_items = FEED_ITEMS

    @lxml_exceptions
    def get_channel_xml_link(self, r_text: str) -> Union[str, None]:
        """Get the RSS feed link from the http response.

        If unusual html response, parsing errors - skip id.

        :param r_text: response from https://www.youtube.com/@username
        :return: feed link
        """
        root = html.fromstring(r_text)
        # <link rel="alternate" type="application/rss+xml" title="RSS" href="https://www.youtube.com/feeds/videos.xml?channel_id=UCxxx">
        xml_url = root.xpath('//link[@type="application/rss+xml"]/@href')  # if not found, then - empty list
        if xml_url:
            return xml_url[0]
        return

    @lxml_exceptions
    def get_xml_feed(self, r_content: bytes):
        """Convert the http response to a lxml object.

        If parsing errors - skip id.

        :param r_content: response from https://www.youtube.com/feeds/videos.xml?...
        :return: instance of <class 'lxml.etree._Element'>
        """
        parser = etree.XMLParser(encoding='UTF-8')
        root = etree.fromstring(r_content, parser=parser)
        return root

    def get_feed_info(self, root, verbose: bool) -> Dict[str, str]:
        """Get information about channel or playlist feed.

        Finds xml tags that contain feed information.

        Channel feed: feed title, channel title, channel url, channel created.
        Playlist feed: feed title, playlist created by, playlist creator url, playlist created.

        If the xml response is unusual (AttributeError if root.find() is None) - CLI stops.

        :param root: instance of <class 'lxml.etree._Element'>
        :param verbose: get more details about the feed
        :return: feed info as a dict
        """
        if verbose:
            published = root.find(self.feed_items['published'])
            if 'channel_id' in root.find(self.feed_items['request_url']).get('href'):
                feed_info = {
                    "feed_type": "CHANNEL FEED",
                    "feed_title": f'{root.find(self.feed_items["feed_title"]).text}',
                    "channel_title": f'{root.find(self.feed_items["channel_name"]).text}',
                    "channel_url": f'{root.find(self.feed_items["channel_uri"]).text}',
                    "channel_created": f'{published.text if published is not None else "No date"}'
                }
            else:
                feed_info = {
                    "feed_type": "PLAYLIST FEED",
                    "feed_title": f'{root.find(self.feed_items["feed_title"]).text}',
                    "playlist_created_by": f'{root.find(self.feed_items["channel_name"]).text}',
                    "playlist_creator_url": f'{root.find(self.feed_items["channel_uri"]).text}',
                    "playlist_created": f'{published.text if published is not None else "No date"}'
                }
        else:
            if 'channel_id' in root.find(self.feed_items['request_url']).get('href'):
                feed_info = {
                    "feed_type": "CHANNEL FEED",
                    "feed_title": f'{root.find(self.feed_items["feed_title"]).text}',
                    "channel_title": f'{root.find(self.feed_items["channel_name"]).text}'
                }
            else:
                feed_info = {
                    "feed_type": "PLAYLIST FEED",
                    "feed_title": f'{root.find(self.feed_items["feed_title"]).text}',
                    "playlist_created_by": f'{root.find(self.feed_items["channel_name"]).text}'
                }
        return feed_info

    def get_feed_videos(self, root, verbose: bool, number: Union[int, None]) -> List[dict]:
        """Get information about feed entries: videos, shorts, live streams.

        Finds xml tags that contain entry data.

        Feed entry: video title, video url, published, views, likes, description.

        If the xml response is unusual (AttributeError if root.find() is None) - CLI stops.

        :param root: instance of <class 'lxml.etree._Element'>
        :param verbose: get more details about the feed entries
        :param number: limit the number of entries for feed (up to 15)
        :return: list of feed entries
        """
        if number:
            # limit the number of entries in the output
            entries = root.findall(self.feed_items['entry'])[0:number]
        else:
            entries = root.findall(self.feed_items['entry'])
        if not entries:  # empty list
            # 'There are no uploads in the feed.'
            return []
        entries_list = []
        for entry in entries:
            if verbose:
                # can be empty
                d = entry.find(self.feed_items['video_description'])
                description = d.text.replace('\n', ' ') if d.text else 'No description'
                e = {
                    "video_title": f'{entry.find(self.feed_items["video_title"]).text}',
                    "video_url": f'{entry.find(self.feed_items["video_link"]).get("href")}',
                    "published": f'{entry.find(self.feed_items["video_published"]).text}',
                    "views": f'{entry.find(self.feed_items["video_views"]).get("views")}',
                    "likes": f'{entry.find(self.feed_items["video_likes"]).get("count")}',
                    "description": f'{description}'
                }
            else:
                e = {
                    "video_title": f'{entry.find(self.feed_items["video_title"]).text}',
                    "video_url": f'{entry.find(self.feed_items["video_link"]).get("href")}',
                    "published": f'{entry.find(self.feed_items["video_published"]).text}'
                }
            entries_list.append(e)

        return entries_list
