from datetime import datetime, timezone
from typing import Generator, Union, List, Dict
from json import dump

from ytfc.utils.request_utils import make_request
from ytfc.utils.xml_utils import get_channel_xml_link, get_xml_feed, get_feed_info, get_feed_videos
from ytfc.utils.html_template import html_begin, html_end, slider_block


def save_text(filename: str, output: Generator[str, None, None], ids: List[str]) -> None:
    """Save the result to a file.

    Creates a text file and saves the result as it was printed.

    :param filename: args.save value
    :param output: result of feed parsing, generated by the generate_output function
    :param ids: a list of IDs from CLI options
    :return: None
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'Feeds\n\nSaved (UTC): {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")}+00:00\n\nYoutube IDs: {", ".join(ids)}\n\n\n')
        for i in output:
            f.write(i)
            f.write('\n')

    
def generate_html(ids: List[str], output: Generator[str, None, None]) -> Generator[str, None, None]:
    """Create an HTML document from the CLI output.

    :param ids: a list of IDs from CLI options
    :param output: result of feed parsing, generated by the generate_output function
    :return: generator, strings that form an HTML document
    """
    html_ids = [f'yt-id{index}' for index, yt_id in enumerate(ids)]
    yield html_begin
    yield f'<h1>Feeds</h1>'
    yield f'<div class="yt-ids"><p>Saved (UTC): {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")}+00:00</p><div>Youtube IDs:</div>'
    for html_id, yt_id in zip(html_ids, ids):
        yield f'<div><a href="#{html_id}">{yt_id}</a></div>'
    yield '</div><br>'  # close yt-ids
    for i in output:
        if i == '\n':
            continue
        # video block - thumbnail, video url (buttons), video title, published, views, likes, description
        elif i.startswith('video title: '):
            video_block = i.split('\n')
            yield '<div class="video-block">'
            # thumbnail
            # In xml - https://i[number].ytimg.com/vi/VIDEO_ID/hqdefault.jpg (480x360).
            # hqdefault.jpg - this is a thumbnail, or the first frame of the video.
            # frames used in html: hqdefault.jpg, hq1.jpg, hq2.jpg, hq3.jpg
            yield slider_block.format(video_id=video_block[1].split("video url: https://www.youtube.com/watch?v=")[1])
            # url
            yield '<div class="video-url">' \
                  f'<button class="video-popup" onclick="openWindow(\'{video_block[1].split("video url: https://www.youtube.com/watch?v=")[1]}\')">' \
                  'open in new window</button>' \
                  f'<button><a href="{video_block[1].split("video url: ")[1]}" target="_blank" rel="noopener noreferrer nofollow">' \
                  'open in new tab</a></button></div>'  # close video-url
            # title
            yield f'<div class="video-title">{video_block[0].split("video title: ", maxsplit=1)[1]}</div>'
            # published
            yield f'<div>{video_block[2]}</div>'
            if len(video_block) > 3:  # verbose
                # views
                yield f'<div>{video_block[3]}</div>'
                # likes
                yield f'<div>{video_block[4]}</div>'
                # description
                if video_block[5] == 'description: No description':
                    yield f'<div>{video_block[5]}</div>'
                else:
                    yield f'<div class="description-popup" onclick="showPopup(event)">show/hide description' \
                          f'<span class="popup-text">{video_block[5].split("description: ", maxsplit=1)[1]}</span></div>'
            yield '<br></div>'  # close video-block
        # yt id
        elif i.startswith('=== '):
            h = i.strip("\n").strip("=").strip(" ")
            yield f'\n<h2 id="{html_ids.pop(0)}">{h}</h2>'
        # feed info: CHANNEL FEED, PLAYLIST FEED
        elif i.startswith(('CHANNEL FEED', 'PLAYLIST FEED')):
            header = i.split('\n')
            yield f'<div class="feed-info">\n<p>{header[0].strip()}</p>'
            for j in header[1:]:
                if j.startswith('channel url: '):
                    u = j.split('channel url: ')[1]
                    yield f'<div>channel url: <a href="{u}" target="_blank" rel="noopener noreferrer nofollow">{u}</a></div>'
                elif j.startswith('playlist creator url: '):
                    u = j.split('playlist creator url: ')[1]
                    yield f'<div>playlist creator url: <a href="{u}" target="_blank" rel="noopener noreferrer nofollow">{u}</a></div>'
                else:
                    yield f'<div>{j}</div>'
            yield '</div><br>'
        # 'Failed to get data from: ', 'Failed to get channel id UCxxx for: ', 'Failed to get feed from: '
        elif i.startswith('Failed to get'):
            u = i.partition(": ")
            yield f'<div class="no-data">{u[0]}: <a href="{u[2].strip()}" target="_blank" rel="noopener noreferrer nofollow">{u[2].strip()}</a></div><br>'
        else:  # There are no uploads in the feed.
            yield f'<div class="no-uploads">{i}</div><br>'
    yield html_end


def save_html(filename: str, output: Generator[str, None, None], ids: List[str]) -> None:
    """Save the result to a file.

    Creates a text file and saves the result as an HTML document.
    
    :param filename: args.save value
    :param output: result of feed parsing, generated by the generate_output function
    :param ids: a list of IDs from CLI options
    :return: None
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for i in generate_html(ids, output):
            f.write(i)
            f.write('\n')


def output_to_dict(ids: List[str], output: Generator[str, None, None]) -> Dict:
    """Create dict from the CLI output.

    Keys and values are strings.

    result = {
        "saved": "Saved (UTC): ...",
        "ids": [str, str, ...],
        "feeds": {
            "<playlist id or channel id or @handle>": {

                # can be empty (error)
                "feed_info": dict,

                # list can be empty (error, no uploads)
                "entries": [dict, dict, ...],

                # only if an error occurred
                "error_message": "...",

                # if there are no uploads in the feed
                "info_message": "..."
            },
            "<playlist id or channel id or @handle>": {...},
        }
    }

    "feed_info": {
        "feed_type": "CHANNEL FEED" or "PLAYLIST FEED",
        "feed_title": "...",
        "channel_title": "..." or "playlist_created_by": "...",
        "channel_url": "..." or "playlist_creator_url": "...", # verbose
        "channel_created": "..." or "playlist_created": "..." # verbose, there may be "No date"
        }

    "entries": list of dicts
        {
        "video_title": "...",
        "video_url":"...",
        "published": "...",
        "views": "...", # verbose
        "likes": "...", # verbose
        "description": "..." or "No description" # verbose
        }

    :param ids: a list of IDs from CLI options
    :param output: result of feed parsing, generated by the generate_output function
    :return: dict to save as a JSON document
    """
    result = {"saved": f'Saved (UTC): {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")}+00:00',
              "ids": ids, "feeds": {}}
    current_id = None
    for i in output:
        if i == '\n':
            continue
        # video block - video url, video title, published, views, likes, description
        elif i.startswith('video title: '):
            video_block = i.split('\n')
            entry = {
                "video_title": video_block[0].split("video title: ", maxsplit=1)[1],
                "video_url": video_block[1].split("video url: ")[1],
                "published": video_block[2].split("published: ")[1]
            }
            if len(video_block) > 3:  # verbose
                entry["views"] = video_block[3].split("views: ")[1]
                entry["likes"] = video_block[4].split("likes: ")[1]
                entry["description"] = video_block[5].split("description: ", maxsplit=1)[1]
            result["feeds"][current_id]["entries"].append(entry)
        # yt id
        elif i.startswith('=== '):
            key = i.strip("\n").strip("=").strip(" ")
            result["feeds"][key] = {
                "feed_info": {},
                "entries": []
            }
            current_id = key
        # feed info: CHANNEL FEED, PLAYLIST FEED
        elif i.startswith(('CHANNEL FEED', 'PLAYLIST FEED')):
            header = i.split('\n')
            feed_info = {
                "feed_type": header[0],
                "feed_title": header[1].split("feed title: ")[1]
            }
            if header[2].startswith('channel title: '):
                # channel title
                feed_info["channel_title"] = header[2].split("channel title: ")[1]
                if len(header) > 3:  # verbose
                    feed_info["channel_url"] = header[3].split("channel url: ")[1]
                    feed_info["channel_created"] = header[4].split("channel created: ")[1]
            elif header[2].startswith('playlist created by: '):
                # playlist created by
                feed_info["playlist_created_by"] = header[2].split("playlist created by: ")[1]
                if len(header) > 3:  # verbose
                    feed_info["playlist_creator_url"] = header[3].split("playlist creator url: ")[1]
                    feed_info["playlist_created"] = header[4].split("playlist created: ")[1]
            result["feeds"][current_id]["feed_info"] = feed_info
        # 'Failed to get data from: ', 'Failed to get channel id UCxxx for: ', 'Failed to get feed from: '
        elif i.startswith('Failed to get'):
            result["feeds"][current_id].update({"error_message": i.strip()})
        else:  # There are no uploads in the feed.
            result["feeds"][current_id].update({"info_message": i})
    # returns dict, object of type generator is not JSON serializable
    return result


def save_json(filename: str, output: Generator[str, None, None], ids: List[str]) -> None:
    """Save the result to a file.

    Creates a text file and saves the result as JSON document.
    
    :param filename: args.save value
    :param output: result of feed parsing, generated by the generate_output function
    :param ids: a list of IDs from CLI options
    :return: None
    """
    d = output_to_dict(ids, output)
    with open(filename, 'w', encoding='utf-8') as f:
        dump(d, f, indent=2)

            
def generate_output(ids: List[str], verbose: bool, number: Union[int, None]) -> Generator[str, None, None]:
    """Display the result of feed parsing.

    :param ids: a list of IDs from CLI options
    :param verbose: args.verbose value, default - False
    :param number: args.number value, default - None
    :return: generator, result of feed parsing
    """
    for channel_or_playlist_id in ids:
        yield f'=== {channel_or_playlist_id} ===\n'
        if channel_or_playlist_id.startswith('@'):
            r_text, status_code = make_request(f'https://www.youtube.com/{channel_or_playlist_id}', 'text')
            # if requests errors, prints error message
            if r_text is None:
                yield f'Failed to get data from: https://www.youtube.com/{channel_or_playlist_id}\n'
                continue
            xml_url = get_channel_xml_link(r_text)
            if not xml_url:
                # parsing errors or id not found in html response
                yield f'Failed to get channel id UCxxx for: https://www.youtube.com/{channel_or_playlist_id}\n'
                continue
        elif channel_or_playlist_id.startswith('UC'):
            xml_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_or_playlist_id}'
        else:
            xml_url = f'https://www.youtube.com/feeds/videos.xml?playlist_id={channel_or_playlist_id}'
        r_content, status_code = make_request(xml_url, 'content')
        # if requests errors, prints error message
        if r_content is None:
            yield f'Failed to get data from: {xml_url}\n'
            continue
        root = get_xml_feed(r_content)
        if root is not None:
            # feed info: CHANNEL FEED, PLAYLIST FEED
            yield get_feed_info(root, verbose)
            yield '\n'
            # generator function
            for i in get_feed_videos(root, verbose, number):
                # video block
                yield i
                yield '\n'
        else:  # parsing errors, prints error message
            yield f'Failed to get feed from: {xml_url}\n'


def redirect_output(ids: List[str], verbose: bool, number: Union[int, None]) -> Generator[str, None, None]:
    """Mediator between functions.

    The result from generate_output goes to save_text or save_html.

    It prints the result of feed parsing line by line
    and returns the result to be saved to a file.
    
    :param ids: a list of IDs from CLI options
    :param verbose: args.verbose value, default - False
    :param number: args.number value, default - None
    :return: generator, strings printed by the CLI
    """
    for i in generate_output(ids, verbose, number):
        print(i)
        yield i
