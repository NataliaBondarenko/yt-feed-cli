from typing import Union, Tuple

import requests

    
def make_request(url: str, response_type: str) -> Tuple[Union[str, bytes, None], int, Union[str, None]]:
    """Request YouTube URLs.
    
    If the request was successful, the function returns response.text or response.content.
    Otherwise, the function returns None.
    Throws an exception for the error that occurred, unless it is a 404.
    URLs that are not found can be skipped. Other errors stop processing the list of IDs.

    :param url: https://www.youtube.com/@username (use 'text') or
                https://www.youtube.com/feeds/videos.xml?... (use 'content')
    :param response_type: 'text' or 'content'
    :return: response or None, response.status_code(for tests), error message or None
    """
    try:
        # allow_redirects=True. If error - r.url in error message, def generate_output gets original url
        r = requests.get(url, timeout=60)
        r.raise_for_status()  # raise requests.HTTPError
        if r.status_code == 200:
            if response_type == 'text':
                result = r.text
                # This channel is not available, status 200, closed by owner, terminated by YouTube, or technical issues
                available = '<link rel="alternate" type="application/rss+xml" title="RSS" ' \
                            'href="https://www.youtube.com/feeds/videos.xml?channel_id=' in result
                if available:
                    return result, r.status_code, None
                else:
                    return (None, r.status_code,
                            f'Unusual response was received for this URL: {r.url}.\n'
                            'This channel may not be available.\n')
            else:  # 'content'
                return r.content, r.status_code, None
        else:
            # treat any unusual status code as a reason to skip processing id
            return (None, r.status_code, f'Unusual status code was received for this URL: {r.url}.\n'
                                         f'{r.status_code}: {r.reason}.\n')
    # 4XX client error or 5XX server error response
    except requests.HTTPError as e:
        code = e.response.status_code
        if code == 404:  # 404  Not Found
            msg = 'The requested playlist ID, channel ID, or @username was not found. \n' \
                  'Maybe there is no such playlist or channel at all, or you made a typo.\n' \
                  f'{e.__class__.__name__}: {e}\n'
            return None, code, msg
        else:
            # for all other HTTP errors
            raise
    # ConnectionError, Timeout, and other errors
    except requests.exceptions.RequestException as e:
        # for all other request errors
        raise
