
from __future__ import unicode_literals,print_function

import hashlib
import logging
import re

logger = logging.getLogger(__name__)

"""
RNZ Magical function
"""


def prog_url(id):
    s = b"%dq6kzN3TQ29ubhUUhdOcirS0fiNITkMMLR5HyU5Sv" % id
    s = hashlib.sha1(s).digest().encode('hex')
    return "http://www.rnz.co.nz/audio/pdata/%s%s.json" % (s, hex(id)[2:])


_cleanr = re.compile('<.*?>')


"""
Returns the audio url for the latest RNZ news bulletin
"""


def get_news_info(download_func):
    r = download_func('http://www.radionz.co.nz/news')

    if r.status_code != 200:
        logger.error('Failed to download %s', 'http://www.radionz.co.nz/news')
        return None

    content = r.text
    content = content[content.find('Latest bulletin'):][:100]
    content = content[content.find('X') + 1:]
    content = content[:content.find('"')]
    code = int(content)
    url = prog_url(code)
    r = download_func(url)

    if r.status_code != 200:
        logger.error("Failed to download: %s", url)
        return None

    data = r.json()
    audio_url = data['item']['audio']['mp3']['url']
    audio_title = data['item']['body']
    audio_title = re.sub(_cleanr, '', audio_title)
    return audio_title,audio_url


if __name__ == '__main__':
    import requests
    print("news url:", get_news_info(requests.get))
