FEED_ITEMS = {
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
