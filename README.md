
This is a CLI utility written in Python. Designed for parsing YouTube RSS feeds.


## How it works


The command-line interface is based on the standard argparse module.

When a user provides a channel or playlist ID, the program requests one of the following URLs:

`https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`  
`https://www.youtube.com/feeds/videos.xml?playlist_id=PLAYLIST_ID`

These links return XML documents for parsing.

If the user specifies `@username`, the program makes an additional request to `https://www.youtube.com/@username` to get a link to the RSS feed. Then it gets the XML document from `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`.

The XML response is parsed using lxml. The main output is information about the feed and a list of feed entries (videos, shorts, live streams).


## Dependencies


- Python 3.7+
- [requests](https://requests.readthedocs.io/en/latest/)
- [lxml](https://lxml.de/)


## Run


Clone repository.
```
git clone https://github.com/NataliaBondarenko/yt-feed-cli.git
```

Change directory to the project directory.
```
cd yt-feed-cli
```

It is recommended to create and activate a [virtual environment](https://docs.python.org/3/library/venv.html). And then install the requirements in the virtual environment.

Install the requirements.
```
python -m pip install -r requirements.txt
```

Try CLI.
```
python -m ytfc <options>
```


## Local project installs


<span style="font-size:0.8em;">See: [pip docs](https://pip.pypa.io/en/stable/topics/local-project-installs/), [setuptools docs](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).</span>

Install the project in editable mode (`pip` version >= 21.3).
```
python -m pip install -e .
```

The dot represents the current folder, which should be the folder where the `pyproject.toml` file is located.


## How to use


Get the list of available options.
```
> ytfc -h
usage: ytfc [-h] [-i ID [ID ...]] [-r FILE] [-n N] [-v] [-s FILE] [-np]

This CLI parses RSS feeds and outputs a list of YouTube videos, shorts, and live streams.

options:
  -h, --help            show this help message and exit
  -i ID [ID ...], --ids ID [ID ...]
                        Channel or playlist IDs for a request.
  -r FILE, --read FILE  File path to a text file containing a list of channel or playlist IDs.
  -n N, --number N      Limit the number of entries in the output.
  -v, --verbose         Display details about the feed and its entries.
  -s FILE, --save FILE  File path to save the results. Creates a txt or html file with the given name.
  -np, --no-print       Skip printing results when saving to a file.
```

Without the `--ids` or `--read` options, the CLI shows usage examples.
```
> ytfc
```

## Main options


### `--ids`, `--read`

The simplest form of use is to specify the IDs of the desired channels or playlists.
```
ytfc -i UCBR8-60-B28hp2BmDPdntcQ UULPBR8-60-B28hp2BmDPdntcQ
```

You can also use `@username`.
```
ytfc -i @youtube
```

Another option is to use a list of identifiers stored in a text file.
```
ytfc -r <local path to text file>
```

Identifiers must be separated by newlines. You can add comments after the # symbol. Example file content:
```
# Channels:

# uploads (@username)
@youtube
# uploads (UC)
UCBR8-60-B28hp2BmDPdntcQ

# Playlists:

# uploads (UU)
UUBR8-60-B28hp2BmDPdntcQ
# videos (UULF)
UULFBR8-60-B28hp2BmDPdntcQ
# live streams (UULV)
UULVBR8-60-B28hp2BmDPdntcQ
# shorts (UUSH)
UUSHBR8-60-B28hp2BmDPdntcQ

# popular videos (UULP)
UULPBR8-60-B28hp2BmDPdntcQ
# popular live streams (UUPV)
UUPVBR8-60-B28hp2BmDPdntcQ
# popular shorts (UUPS)
UUPSBR8-60-B28hp2BmDPdntcQ

# members-only videos (UUMO, UUMF)
# members-only live streams (UUMV)
# members-only shorts (UUMS)

# regular playlist (PL)
PLbpi6ZahtOH7MBdd2q811v_7Tu31vnsyq
```

Both options, `--read` and `--ids`, can be used at the same time. In this case, the identifiers from the file will be merged with the manually entered identifiers into a single list. All other options will be applied to this list.
```
ytfc -i @youtube -r <local path to text file> -n 1 -v
```


## Additional options


### `--number`

Limit the number of entries in the output. The number of entries in the RSS feed is up to 15.
```
ytfc -i @youtube -n 5
```


### `--verbose`

The `--verbose` option displays details about feed entries.
```
ytfc -i UULPBR8-60-B28hp2BmDPdntcQ -n 1 -v
```

Output:
```
=== UULPBR8-60-B28hp2BmDPdntcQ ===

PLAYLIST FEED
feed title: Popular videos
playlist created by: YouTube
playlist creator url: https://www.youtube.com/channel/UCBR8-60-B28hp2BmDPdntcQ
playlist created: 2021-10-13T12:16:00+00:00


video title: YouTube Rewind: The Ultimate 2016 Challenge | #YouTubeRewind
video url: https://www.youtube.com/watch?v=_GuOjXYl5ew
published: 2016-12-07T18:00:03+00:00
views: 245488982
likes: 4109862
description: YouTube Rewind 2016. Celebrating ...
```

Output without `--verbose` option:
```
=== UULPBR8-60-B28hp2BmDPdntcQ ===

PLAYLIST FEED
feed title: Popular videos
playlist created by: YouTube


video title: YouTube Rewind: The Ultimate 2016 Challenge | #YouTubeRewind
video url: https://www.youtube.com/watch?v=_GuOjXYl5ew
```


### `--save`

Save the result to a file.

Creates a text file and saves the result as it was printed.
```
ytfc -i @youtube -s <local path>/output.txt
```

Creates a text file and saves the result as an HTML document. Feed entries will be embedded in the HTML code.
```
ytfc -i @youtube -s <local path>/output.html
```


### `--no-print`

Skip printing results when saving to a file. If errors occur, error messages will still be printed.

```
ytfc -i @youtube -s <local path>/output.txt -np
```

```
ytfc -i @youtube -s <local path>/output.html -np
```