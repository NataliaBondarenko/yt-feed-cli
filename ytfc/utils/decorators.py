from functools import wraps

from lxml import etree


def python_exceptions(func):
    """Interception of the Python exceptions.
    Used as decorator for def main().

    If the xml response is unusual, there will be Python errors in xml_utils functions.
    AttributeError if root.find() is None.
    
    :param func: executable function
    :return: CLI stops
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print('The execution of the program was interrupted.')
        except Exception as e:
            print('Unfortunately, an unexpected error occurred while retrieving the data.')
            print(f'{e.__class__.__name__}: {e}.')
    return wrapper


def lxml_exceptions(func):
    """Interception of the lxml exceptions.
    Used as decorator for get_channel_xml_link() and get_xml_feed().

    :param func: executable function
    :return: CLI continues processing the next ID in the list
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except etree.LxmlError as e:  # etree.ParserError, etree.XMLSyntaxError
            # XML - get_xml_feed(r_content)
            # HTML - get_channel_xml_link(r_text)
            response = 'XML' if func.__name__ == 'get_xml_feed' else 'HTML'
            print(f'Unable to parse {response} response.')
            print(f'{e.__class__.__name__}: {e}\n')
    return wrapper
