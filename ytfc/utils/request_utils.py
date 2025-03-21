from typing import Union, Tuple

import requests

    
def make_request(url: str, response_type: str) -> Tuple[Union[str, bytes, None], int]:
    """Request YouTube URLs.

    URLs
    https://www.youtube.com/@username (html, 'text')
    https://www.youtube.com/feeds/videos.xml?... (xml, 'content')
    
    If the request was successful, the function returns response.text or response.content.
    Otherwise, the function returns None.
    
    :param url: URLs
    :param response_type: 'text' or 'content'
    :return: response or None, response.status_code for tests
    """
    try:
        # allow_redirects=True. If error - r.url in error message, def generate_output yields original url
        r = requests.get(url, timeout=60)
        r.raise_for_status()  # raise requests.HTTPError
        # html or xml
        result = r.text if response_type == 'text' else r.content
        if r.status_code == 200 and result:
            return result, r.status_code
        else:
            print(f'No content was retrieved from the specified URL: {r.url}.')
            print(r.status_code, r.reason, '\n')
            return None, r.status_code
    # 4XX client error or 5XX server error response
    except requests.HTTPError as e:
        code = r.status_code
        if code == 404:  # 404  Not Found
            print('The requested playlist ID, channel ID, or @username was not found.\n'
                  'Maybe there is no such playlist or channel at all, or you made a typo.')
        elif code == 500:  # 500 Internal Server Error
            print('YouTube.com is currently unable to fulfill the request.')
        # for all HTTP errors
        print(f'{e.__class__.__name__}: {e}\n')
        return None, code
    # ConnectionError, Timeout, and other errors
    except requests.exceptions.RequestException as e:
        print(f'{e.__class__.__name__}: {e}\n')
        return None, r.status_code
