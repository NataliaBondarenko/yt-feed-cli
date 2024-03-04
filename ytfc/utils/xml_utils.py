from typing import Generator, Union

from lxml import etree, html

from ytfc.utils.decorators import lxml_exceptions


feed_items = {
    # root.find()
    'request_url': '{http://www.w3.org/2005/Atom}link',
    'feed_title': '{http://www.w3.org/2005/Atom}title',
    'channel_name': '{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name',
    'channel_uri': '{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}uri',
    # when a channel or playlist is created, not available for mixes
    'published': '{http://www.w3.org/2005/Atom}published',
    # there may be no entries in the feed (no uploads)
    'entry': '{http://www.w3.org/2005/Atom}entry',
    
    # entry.find()
    'video_title': '{http://www.w3.org/2005/Atom}title',
    'video_link': '{http://www.w3.org/2005/Atom}link',
    'video_published': '{http://www.w3.org/2005/Atom}published',
    # description of the video may or may not be
    'video_description': '{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}description',
    'video_likes': '{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}community/{http://search.yahoo.com/mrss/}starRating',
    'video_views': '{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}community/{http://search.yahoo.com/mrss/}statistics'
    }


@lxml_exceptions
def get_channel_xml_link(r_text: str) -> Union[str, None]:
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
def get_xml_feed(r_content: bytes):
    """Convert the http response to a lxml object.

    If parsing errors - skip id.
    
    :param r_content: response from https://www.youtube.com/feeds/videos.xml?...
    :return: instance of <class 'lxml.etree._Element'>
    """
    parser = etree.XMLParser(encoding='UTF-8')
    root = etree.fromstring(r_content, parser=parser)
    return root


def get_feed_info(root, verbose: bool) -> str:
    """Get information about channel or playlist feed.

    Finds xml tags that contain feed information.
    
    Channel feed:
    feed title, channel title, channel url, channel created
    Playlist feed:
    feed title, playlist created by, playlist creator url,
    playlist created

    If the xml response is unusual (AttributeError if root.find() is None) - CLI stops.
    
    :param root: instance of <class 'lxml.etree._Element'>
    :param verbose: args.verbose value, default - False
    :return: feed info as a string
    """
    if verbose:
        published = root.find(feed_items['published'])
        if 'channel_id' in root.find(feed_items['request_url']).get('href'):
            feed_info = 'CHANNEL FEED\n' \
                        f'feed title: {root.find(feed_items["feed_title"]).text}\n' \
                        f'channel title: {root.find(feed_items["channel_name"]).text}\n' \
                        f'channel url: {root.find(feed_items["channel_uri"]).text}\n' \
                        f'channel created: {published.text if published is not None else "No date"}'
        else:
            feed_info = 'PLAYLIST FEED\n' \
                        f'feed title: {root.find(feed_items["feed_title"]).text}\n' \
                        f'playlist created by: {root.find(feed_items["channel_name"]).text}\n' \
                        f'playlist creator url: {root.find(feed_items["channel_uri"]).text}\n' \
                        f'playlist created: {published.text if published is not None else "No date"}'
    else:
        if 'channel_id' in root.find(feed_items['request_url']).get('href'):
            feed_info = 'CHANNEL FEED\n' \
                        f'feed title: {root.find(feed_items["feed_title"]).text}\n' \
                        f'channel title: {root.find(feed_items["channel_name"]).text}'
        else:
            feed_info = 'PLAYLIST FEED\n' \
                        f'feed title: {root.find(feed_items["feed_title"]).text}\n' \
                        f'playlist created by: {root.find(feed_items["channel_name"]).text}'
    return feed_info
        
    
def get_feed_videos(root, verbose: bool, number: Union[int, None]) -> Generator[str, None, None]:
    """Get information about feed entries: videos, shorts, live streams.

    Finds xml tags that contain entry data.

    Entry data:
    video title, video url, published, views, likes, description.

    If the xml response is unusual (AttributeError if root.find() is None) - CLI stops.
    
    :param root: instance of <class 'lxml.etree._Element'>
    :param verbose: args.verbose value, default - False
    :param number: args.number value, default - None
    :return: generator, data for each entry as a string
    """    
    if number:
        # limit the number of entries in the output
        entries = root.findall(feed_items['entry'])[0:number]
    else:
        entries = root.findall(feed_items['entry'])
    if not entries:  # empty list
        yield 'There are no uploads in the feed.'
    for entry in entries:
        if verbose:
            # can be empty
            d = entry.find(feed_items['video_description'])
            description = d.text.replace('\n', ' ') if d.text else 'No description'
            yield f'video title: {entry.find(feed_items["video_title"]).text}\n' \
                  f'video url: {entry.find(feed_items["video_link"]).get("href")}\n' \
                  f'published: {entry.find(feed_items["video_published"]).text}\n' \
                  f'views: {entry.find(feed_items["video_views"]).get("views")}\n' \
                  f'likes: {entry.find(feed_items["video_likes"]).get("count")}\n' \
                  f'description: {description}'
        else:
            yield f'video title: {entry.find(feed_items["video_title"]).text}\n' \
                  f'video url: {entry.find(feed_items["video_link"]).get("href")}'
