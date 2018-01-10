from __future__ import unicode_literals

import logging
import os
import pykka
import requests
import requests_cache
from dateutil.parser import parse as parse_date
from mopidy import backend, httpclient
from mopidy.models import Ref, Artist, Album, Track

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

        logging.debug('user_agent: %s', full_user_agent)

        self.session.headers.update({'user-agent': full_user_agent})

        # def on_start(self):
        # self.library.get_podcasts()

    def download(self, url):
        return self.session.get(url)


def _duration(s):
    s = s.split(':')
    duration = int(s[-1])
    i = len(s)
    if i > 1:
        duration += 60 * int(s[-2])
    if i > 2:
        duration += 60 * 60 * int(s[-3])
    return duration



class RNZLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='rnz:root', name='RNZ')
    PODCASTS_URI = 'https://h1.danbrough.org/data/podcastinfo_v1.json'
    NAMESPACES = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    podcast_items = {}

    def browse(self, uri):
        logger.debug("browse() %s for backend: %s", uri, self.backend)
        result = []

        if not uri.startswith('rnz:'):
            return result

        if uri == 'rnz:root':
            result.append(Ref.track(name='Latest News Bulletin', uri='rnz:news'))
            result.append(Ref.directory(name='Streams', uri='rnz:streams'))
            result.append(Ref.directory(name='Podcasts', uri='rnz:podcasts'))
            return result

        if uri == 'rnz:streams':
            return [
                Ref.track(
                    name=stream.name,
                    uri='rnz:stream:%s' % stream.name
                ) for stream in content.streams
            ]

        if uri == 'rnz:podcasts':
            return [
                Ref.directory(
                    name=podcast['title'],
                    uri='rnz:podcast:%s' % podcast['title']
                ) for podcast in self.get_podcasts()
            ]

        if uri.startswith('rnz:podcast:'):
            title = uri[12:]
            podcast = self.podcasts_map[title]
            podcast_url = podcast['urls']
            r = self.download(podcast_url)

            if r.status_code != 200:
                logging.error("failed to download %s", podcast_url)
                return None

            tree = ET.fromstring(r.text.encode('utf-8'))

            album = Album(
                artists=[Artist(name='RNZ')],
                images=[podcast['imageURL']],
                name=podcast['title'],
            )

            for item in tree.iter('item'):
                title = item.find('title').text.strip()
                logger.debug("got title %s", title)

                duration = item.find('itunes:duration', self.NAMESPACES)

                if duration is not None:
                    logger.debug("got duration %s", duration.text.strip())

                track_url = item.find('enclosure').get('url')

                result.append(Ref.track(
                    name=title,
                    uri='rnz:podcast_item:%s' % track_url,
                ))

                track_date = item.find('pubDate').text.strip()
                logger.debug("track_date: %s",track_date)
                track_date = parse_date(track_date).strftime('%Y-%m-%d')

                self.podcast_items[track_url] = Track(
                    name=title,
                    album=album,
                    artists=[Artist(name='RNZ')],
                    uri=track_url,
                    comment=item.find('description').text.strip(),
                    date=track_date,
                    length=_duration(
                        item.find('itunes:duration', self.NAMESPACES).text.strip()) * 1000
                )
            return result

        return []

    # def get_images(self, uris):
    #     logger.info('get_images(): %s',uris)
    #     # if len(uris) == 0 and uris[0] == 'rnz:news':
    #     #     pass
    #
    #     return super(RNZLibraryProvider,self).get_images(uris)

    def lookup(self, uri):
        logger.debug("lookup() %s", uri)
        result = []

        if not uri.startswith('rnz:'):
            return result

        if uri == 'rnz:news':
            from .news import get_news_info
            title, url, duration = get_news_info(self.download)
            return [
                content.news_track.replace(uri=url).replace(name=title).replace(length=duration)]

        if uri == 'rnz:streams':
            return content.streams

        if uri.startswith('rnz:stream:'):
            return [content.stream_map[uri[11:]]]

        if uri.startswith('rnz:podcast:'):
            return [self.podcasts_map[uri[12:]]]

        if uri.startswith('rnz:podcast_item:'):
            return [self.podcast_items[uri[17:]]]

        return result

    def download(self, url):
        logger.info("RNZLibraryProvider::download() url:%s", url)
        return self.backend.download(url)

    def get_podcasts(self):
        r = self.download(RNZLibraryProvider.PODCASTS_URI)
        if r.status_code != 200:
            logger.error("RNZ: Failed to download %s", RNZLibraryProvider.PODCASTS_URI)
            return []
        podcasts = r.json()
        for podcast in podcasts:
            title = podcast['title']
            if title.startswith('RNZ: '): podcast['title'] = title[4:].strip()
        self.podcasts = sorted(podcasts, key=lambda x: x['title'])
        self.podcasts_map = {podcast['title']: podcast for podcast in self.podcasts}
        logger.info("RNZ: Discovered %d podcasts", len(podcasts))
        return self.podcasts
