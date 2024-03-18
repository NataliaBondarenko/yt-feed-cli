from typing import Tuple, Union, List

from ytfc.utils.regex_patterns import (USERNAME_PATTERN, CHANNEL_PATTERN, PL_PATTERN,
                                       RD_PATTERN, OL_PATTERN, RDCLAK_PATTERN)


def open_file(path: str) -> List[str]:
    """Reading identifiers from a text file.

    Used in def check_ids.

    :param path: path to a text file with a list of channel or playlists IDs
    :return: a list of IDs
    """
    yt_ids = []
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
        for i in lines:
            i = i.strip()
            # skip comments and newlines
            if i == '' or i.startswith('#'):
                continue
            yt_ids.append(i)
    return yt_ids


def check_duplicates(ids: List[str]) -> List[str]:
    """Checks the list of IDs for duplicates.

    @username is case-insensitive.
    Other identifiers are case-sensitive.

    :param ids: a list of IDs
    :return: a list of IDs that do not contain duplicates
    """
    yt_ids = []
    for i in ids:
        if i.startswith('@'):
            i = i.lower()
        if i not in yt_ids:
            yt_ids.append(i)
        else:
            continue
    return yt_ids


def check_ids(ids: List[str], path: str) -> Union[Tuple[List[str], None], Tuple[None, List[str]]]:
    """A simple check to see if an ID contains allowed characters.

    @username (handle):
      https://support.google.com/youtube/answer/11585688
    Channel ID:
      UC + 22 characters.
    IDs based on channel ID:
      UU, FL, UULF, UULV, UUSH, UULP, UUPV, UUPS, UUMO, UUMF, UUMV, UUMS + 22
    PL:
      The shortest playlist identifier is PL + 16. Newer IDs are PL + 32.
    RD and OL:
      Mix IDs or album/music playlist IDs vary in length.
      Minimum mix ID is RD + 11 (video id).
      Music:
      OLAK5uy_[klmn]{1}[A-Za-z0-9_-]{32}
      RDCLAK5uy_[klmn]{1}[A-Za-z0-9_-]{32}
    
    :param ids: args.ids, a list of IDs
    :param path: args.read, path to a text file with a list of channel or playlists IDs
    :return: a list of IDs that do not pass validation and None
             or
             None and a list of IDs that pass validation
    """
    if ids and path:
        path_ids = open_file(path)
        yt_ids = ids + path_ids
    elif path:
        yt_ids = open_file(path)
    elif ids:
        yt_ids = ids
    invalid_ids = []
    
    for i in yt_ids:
        if i.startswith('@'):
            m = USERNAME_PATTERN.match(i)
        elif i.startswith(('UC', 'UU', 'FL')):
            m = CHANNEL_PATTERN.match(i)
        elif i.startswith('PL'):
            m = PL_PATTERN.match(i)
        elif i.startswith('RDCLAK5uy_'):
            m = RDCLAK_PATTERN.match(i)
        elif i.startswith('RD'):
            m = RD_PATTERN.match(i)
        elif i.startswith('OLAK5uy_'):
            m = OL_PATTERN.match(i)
        else:
            m = None
        if m:
            continue
        else:
            invalid_ids.append(i)
    if invalid_ids:
        return invalid_ids, None
    else:
        return None, check_duplicates(yt_ids)
