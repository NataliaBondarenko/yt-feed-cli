from datetime import datetime, timezone
from typing import Union, List, Dict
from json import dump

from ytfc.utils.request_utils import make_request
from ytfc.utils.xml_utils import XMLHandler
from ytfc.utils.html_template import html_begin, html_end, slider_block, buttons_block


class Output:
    def __init__(self, ids: List[str]):
        self.xml_handler = XMLHandler()
        self.ids = ids
        self.output = None

    def _create_base_dict(self) -> Dict:
        """Create dict to save feeds.

        Example of filled dict:
        self.output = {
            "created_utc": "...",
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

        :return: dict
        """
        base_dict = {
            "created_utc": f'{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")}+00:00',
            "ids": self.ids,
            "feeds": {k: {"feed_info": {}, "entries": []} for k in self.ids}
        }
        return base_dict

    def generate_output(self, *, verbose: bool, number: Union[int, None], no_print: bool, save: bool) -> None:
        """Display and store the results of feed parsing for list of ids.

        :param verbose: get more details about the feed and its entries
        :param number: limit the number of entries for each feed (up to 15)
        :param no_print: print feed info and entries or not
        :param save: save feed info and entries to self.output or not
        :return: None
        """
        if not save and no_print:
            raise ValueError(f'Invalid argument combination: save={save}, no_print={no_print}. '
                             'Not saving and not printing output at the same time')
        if save:
            self.output = self._create_base_dict()
        for channel_or_playlist_id in self.ids:
            if not no_print:
                print(f'\n=== {channel_or_playlist_id} ===\n')
            if channel_or_playlist_id.startswith('@'):
                r_text, status_code, error_msg = make_request(f'https://www.youtube.com/{channel_or_playlist_id}', 'text')
                # if requests errors, prints error message
                if r_text is None:
                    if save:
                        self.output["feeds"][channel_or_playlist_id].update(
                            {"error_message": f'Failed to get data from: https://www.youtube.com/{channel_or_playlist_id}'})
                    if not no_print:
                        print(error_msg)
                    print(f'Failed to get data from: https://www.youtube.com/{channel_or_playlist_id}\n')
                    continue
                xml_url = self.xml_handler.get_channel_xml_link(r_text)
                if not xml_url:
                    # parsing errors or id not found in html response
                    if save:
                        self.output["feeds"][channel_or_playlist_id].update(
                            {"error_message": f'Failed to get channel id UCxxx for: https://www.youtube.com/{channel_or_playlist_id}'})
                    print(f'Failed to get channel id UCxxx for: https://www.youtube.com/{channel_or_playlist_id}\n')
                    continue
            elif channel_or_playlist_id.startswith('UC'):
                xml_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_or_playlist_id}'
            else:
                xml_url = f'https://www.youtube.com/feeds/videos.xml?playlist_id={channel_or_playlist_id}'
            r_content, status_code, error_msg = make_request(xml_url, 'content')
            # if requests errors, prints error message
            if r_content is None:
                if save:
                    self.output["feeds"][channel_or_playlist_id].update(
                        {"error_message": f'Failed to get data from: {xml_url}'})
                if not no_print:
                    print(error_msg)
                print(f'Failed to get data from: {xml_url}\n')
                continue
            root = self.xml_handler.get_xml_feed(r_content)
            if root is not None:
                # feed info: CHANNEL FEED, PLAYLIST FEED
                info = self.xml_handler.get_feed_info(root, verbose)  # dict
                if save:
                    self.output["feeds"][channel_or_playlist_id]["feed_info"] = info
                if not no_print:
                    for k, v in info.items():
                        print(f'{k.replace("_", " ")}: {v}')
                    print()
                entries = self.xml_handler.get_feed_videos(root, verbose, number)  # list of dicts
                if not entries:
                    if save:
                        self.output["feeds"][channel_or_playlist_id].update(
                            {"info_message": "There are no uploads in the feed."})
                    if not no_print:
                        print('There are no uploads in the feed.\n')
                else:
                    if save:
                        self.output["feeds"][channel_or_playlist_id]["entries"] = entries
                    if not no_print:
                        for i in entries:
                            for k, v in i.items():
                                print(f'{k.replace("_", " ")}: {v}')
                            print()
            else:
                # parsing errors
                if save:
                    self.output["feeds"][channel_or_playlist_id].update(
                        {"error_message": f'Failed to get feed from: {xml_url}'})
                print(f'Failed to get feed from: {xml_url}\n')

    def save_to_file(self, filename: str):
        raise NotImplementedError


class TXTOutput(Output):
    def save_to_file(self, filename: str) -> None:
        """Creates a text file and saves the output.

        self.output - result of feed parsing, created by the generate_output function.

        :param filename: "path/to/file.txt", args.save value
        :return: None
        """
        if self.output is None:
            raise TypeError('There is nothing to save to file. '
                            'Use self.generate_output(<verbose>, <number>, <no_print>, save=True) first.')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Feeds\n")
            f.write(f'Created (UTC):{self.output["created_utc"]}\n')
            f.write(f'Youtube IDs: {", ".join(self.ids)}\n\n')
            for k, v in self.output["feeds"].items():
                f.write(f'\n=== {k} ===\n\n')
                # feed info: CHANNEL FEED, PLAYLIST FEED
                if v["feed_info"]:
                    for ik, iv in v["feed_info"].items():
                        f.write(f'{ik.replace("_", " ")}: {iv}\n')
                    f.write('\n\n')
                # videos
                if v["entries"]:
                    for entry in v["entries"]:
                        for ek, ev in entry.items():
                            f.write(f'{ek.replace("_", " ")}: {ev}\n')
                        f.write('\n')
                if v.get("info_message"):
                    f.write(f'{v["info_message"]}\n')
                if v.get("error_message"):
                    f.write(f'{v["error_message"]}\n')
                f.write('\n')


class HTMLOutput(Output):
    def save_to_file(self, filename: str) -> None:
        """Creates a text file and saves the result as an HTML document.

        self.output - result of feed parsing, created by the generate_output function.

        :param filename: "path/to/file.html", args.save value
        :return: None
        """
        if self.output is None:
            raise TypeError('There is nothing to save to file. '
                            'Use self.generate_output(<verbose>, <number>, <no_print>, save=True) first.')
        with open(filename, 'w', encoding='utf-8') as f:
            html_ids = [f'yt-id{index}' for index, yt_id in enumerate(self.ids)]
            f.write(f'{html_begin}\n')
            f.write("<h1>Feeds</h1>\n")
            f.write(f'<div class="yt-ids"><p>Created (UTC): {self.output["created_utc"]}</p>')
            f.write('<div>Youtube IDs:</div>')
            for html_id, yt_id in zip(html_ids, self.ids):
                f.write(f'<div><a href="#{html_id}">{yt_id}</a></div>')
            f.write('</div><br>\n')  # close yt-ids

            # feed info: CHANNEL FEED, PLAYLIST FEED
            for k, v in self.output["feeds"].items():
                f.write(f'<h2 id="{html_ids.pop(0)}">{k}</h2>\n')
                verbose = len(v["feed_info"]) > 3
                if v["feed_info"]:
                    f.write(f'<div class="feed-info"><div>feed type: {v["feed_info"]["feed_type"]}</div>')
                    f.write(f'<div>feed title: {v["feed_info"]["feed_title"]}</div>')
                    if v["feed_info"].get("channel_title"):
                        f.write(f'<div>channel title: {v["feed_info"]["channel_title"]}</div>')
                        if verbose:
                            f.write(f'<div>channel url: <a href="{v["feed_info"]["channel_url"]}" target="_blank" '
                                    f'rel="noopener noreferrer nofollow">{v["feed_info"]["channel_url"]}</a></div>')
                            f.write(f'<div>channel created: {v["feed_info"]["channel_created"]}</div>')
                    if v["feed_info"].get("playlist_created_by"):
                        f.write(f'<div>playlist created by: {v["feed_info"]["playlist_created_by"]}</div>')
                        if verbose:
                            f.write(f'<div>playlist creator url: <a href="{v["feed_info"]["playlist_creator_url"]}" '
                                    'target="_blank" rel="noopener noreferrer nofollow">'
                                    f'{v["feed_info"]["playlist_creator_url"]}</a></div>')
                            f.write(f'<div>playlist created: {v["feed_info"]["playlist_created"]}</div>')
                    f.write('</div><br>\n')  # close feed-info
                if v["entries"]:
                    for entry in v["entries"]:
                        # video block:
                        # thumbnail, video url (buttons), video title, published, views, likes, description
                        f.write('<div class="video-block">\n')
                        # thumbnail
                        # In xml - https://i[number].ytimg.com/vi/VIDEO_ID/hqdefault.jpg (480x360).
                        # hqdefault.jpg - this is a thumbnail, or the first frame of the video.
                        # frames used in html: hqdefault.jpg, hq1.jpg, hq2.jpg, hq3.jpg
                        f.write(slider_block.format(
                            video_id=entry["video_url"].split("https://www.youtube.com/watch?v=")[1]))
                        # url
                        f.write(buttons_block.format(
                            video_id=entry["video_url"].split("https://www.youtube.com/watch?v=")[1],
                            video_url=entry["video_url"]))  # close video-url
                        # title
                        f.write(f'<div class="video-title">{entry["video_title"]}</div>\n')
                        # published
                        f.write(f'<div>published: {entry["published"]}</div>')
                        if verbose:
                            # views
                            f.write(f'\n<div>views: {entry["views"]}</div>')
                            # likes
                            f.write(f'<div>likes: {entry["likes"]}</div>\n')
                            # description
                            if entry["description"] == 'No description':
                                f.write(f'<div>description: {entry["description"]}</div>')
                            else:
                                f.write(
                                    '<div class="description-popup" onclick="showPopup(event)">show/hide description'
                                    f'<span class="popup-text">{entry["description"]}</span></div>')
                        f.write('<br></div>\n')  # close video-block
                # There are no uploads in the feed.
                if v.get("info_message"):
                    f.write(f'<div class="no-uploads">{v["info_message"]}</div><br>\n')
                # 'Failed to get data from: ', 'Failed to get channel id UCxxx for: ', 'Failed to get feed from: '
                if v.get("error_message"):
                    u = v["error_message"].partition(": ")
                    f.write(f'<div class="no-data">{u[0]}: <a href="{u[2]}" '
                            f'target="_blank" rel="noopener noreferrer nofollow">{u[2]}</a></div><br>\n')
            f.write(html_end)


class JSONOutput(Output):
    def save_to_file(self, filename: str) -> None:
        """Creates a text file and saves the result as JSON document.

        self.output - result of feed parsing, created by the generate_output function.

        :param filename: "path/to/file.json", args.save value
        :return: None
        """
        if self.output is None:
            raise TypeError('There is nothing to save to file. '
                            'Use self.generate_output(<verbose>, <number>, <no_print>, save=True) first.')
        with open(filename, 'w', encoding='utf-8') as f:
            dump(self.output, f, indent=2)
