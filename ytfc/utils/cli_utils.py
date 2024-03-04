from typing import Tuple, Union, List


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
            # skip comments and newlines
            if i == '\n' or i.startswith('#'):
                continue
            yt_ids.append(i.strip())
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
    """A simple check to see if an ID starts with allowed characters.

    Channel prefixes:
    @, UC
    Playlist prefixes:
    PL, UU, RD, OL, FL
    [-_0-9A-Za-z]
    
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
        if i.startswith(('@', 'UC', 'PL', 'UU', 'RD', 'OL', 'FL')):
            continue
        else:
            invalid_ids.append(i)
    if invalid_ids:
        return invalid_ids, None
    else:
        return None, check_duplicates(yt_ids)
