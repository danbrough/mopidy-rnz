from __future__ import unicode_literals

import requests
import requests_cache
import logging
import os
import pykka
import re
from mopidy import backend,httpclient
from mopidy.models import Ref, Artist, Album,Track
import mopidy_rnz

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


from mopidy_rnz import content

class RNZBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(RNZBackend, self).__init__()
        self.library = RNZLibraryProvider(backend=self)
        self.uri_schemes = ['rnz']

        http_cache = config['rnz']['http_cache']
        http_cache = os.path.expanduser(http_cache)
        logging.info("http_cache: %s", http_cache)
        requests_cache.install_cache(http_cache, backend='sqlite', expire_after=300)

        proxy_config = config['proxy']

        self.session = requests.Session()
        if proxy_config is not None:
          proxy = httpclient.format_proxy(proxy_config)
          self.session.proxies.update({'http': proxy, 'https': proxy})

        full_user_agent = httpclient.format_user_agent("%s/%s" % (
          mopidy_rnz.Extension.dist_name,
          mopidy_rnz.__version__))

        logging.debug('user_agent: %s',full_user_agent)

        self.session.headers.update({'user-agent': full_user_agent})

    def on_start(self):
        self.library.get_podcasts()

    def download(self, url):
        return self.session.get(url)


class RNZLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='rnz:root', name='RNZ')
    PODCASTS_URI = 'https://h1.danbrough.org/data/podcastinfo_v1.json'
    podcasts = []
    podcast_items = []
    match_podcast = re.compile(r'rnz:podcasts:\d+$')
    match_podcast_items = re.compile(r'rnz:podcasts:\d+:\d+$')

    def browse(self, uri):
        logger.info("browse() %s for backend: %s", uri,self.backend)
        result = []

        if not uri.startswith('rnz:'):
            return result

        if uri == 'rnz:root':
            result.append(Ref.directory(name='Streams', uri='rnz:streams'))
            result.append(Ref.directory(name='Podcasts', uri='rnz:podcasts'))
            result.append(Ref.track(name='Latest News Bulletin', uri='rnz:news'))
            return result

        if uri == 'rnz:streams':
            for stream in content.streams:
                result.append(
                    Ref.track(
                        name=stream.name,
                        uri='rnz:streams:%i' % len(result)
                    ))
            return result

        if uri == 'rnz:podcasts':
            podcasts = self.get_podcasts()
            for n in range(len(podcasts)):
                title = podcasts[n]['title']
                if title.startswith('RNZ: '): title = title[4:]
                result.append(Ref.directory(
                    name=title,
                    uri='rnz:podcasts:%i' % n
                ))
            return result

        if self.match_podcast.match(uri):
            index = int(uri[uri.rfind(':') + 1:])
            self.podcast_items = []
            podcast = self.get_podcasts()[index]
            podcast_url = podcast['urls']
            r = self.download(podcast_url)
            if r.status_code != 200:
                logging.error("failed to download %s", podcast_url)
                return None
            tree = ET.fromstring(r.text.encode('utf-8'))

            album= Album(
                artists = [Artist(name='RNZ')],
                images = [podcast['imageURL']],
                name = podcast['title'],
            )

            for item in tree.iter('item'):
                title = item.find('title').text.strip()
                result.append(Ref.track(
                    name=title,
                    uri='%s:%i' % (uri, len(result)),
                ))
                self.podcast_items.append(Track(
                    name=title,
                    album = album,
                    uri=item.find('enclosure').get('url'),
                    comment = item.find('description').text.strip(),
                ))
            return result

        return []

    def lookup(self, uri):
        logger.info("lookup() %s", uri)
        result = []

        if not uri.startswith('rnz:'):
            return result

        if uri == 'rnz:news':
            from .news import get_news_info
            title, url = get_news_info(self.download)
            return [content.news_track.replace(uri=url).replace(name=title)]

        if uri == 'rnz:streams':
            return content.streams

        if uri.startswith('rnz:streams:'):
            return [content.streams[int(uri.split(':')[-1])]]

        if self.match_podcast_items.match(uri):
            return [self.podcast_items[int(uri[uri.rfind(':')+1:])]]

        return result


    def download(self, url):
        logger.info("RNZLibraryProvider::download() url:%s", url)
        return self.backend.download(url)

    def get_podcasts(self):
        if self.podcasts: return self.podcasts
        r = self.download(RNZLibraryProvider.PODCASTS_URI)
        if r.status_code != 200:
            logger.error("RNZ: Failed to download %s", RNZLibraryProvider.PODCASTS_URI)
            return []
        self.podcasts = r.json()
        logger.info("RNZ: discovered %d podcasts", len(self.podcasts))
        return self.podcasts

