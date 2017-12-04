from __future__ import unicode_literals

import httplib2
import json
import logging
import os
import pykka
import re
from mopidy import backend
from mopidy.models import Ref, Artist, Album,Track

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

httplib2.debuglevel = 5

from mopidy_rnz import content

class RNZBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(RNZBackend, self).__init__()
        self.library = RNZLibraryProvider(backend=self)
        self.uri_schemes = ['rnz']

        cache_dir = config['rnz']['cache_dir']
        cache_dir = os.path.expanduser(cache_dir)
        logging.info("cache_dir: %s", cache_dir)
        self.http_cache = httplib2.Http(cache_dir)
        proxy_config = config['proxy']

        # self.session = requests.Session()
        # if proxy_config is not None:
        #   proxy = httpclient.format_proxy(proxy_config)
        #   self.session.proxies.update({'http': proxy, 'https': proxy})
        #
        # full_user_agent = httpclient.format_user_agent("%s/%s" % (
        #   mopidy_rnz.Extension.dist_name,
        #   mopidy_rnz.__version__))
        # self.session.headers.update({'user-agent': full_user_agent})

    def on_start(self):
        self.library.get_podcasts()

    def download(self, url):
        return self.http_cache.request(url)




class RNZLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='rnz:root', name='RNZ')
    PODCASTS_URI = 'https://h1.danbrough.org/data/podcastinfo_v1.json'
    podcasts = []
    podcast_items = []
    match_podcast = re.compile(r'rnz:podcasts:\d+$')
    match_podcast_items = re.compile(r'rnz:podcasts:\d+:\d+$')

    def browse(self, uri):
        logger.info("browse() %s", uri)
        result = []

        if not uri.startswith('rnz:'):
            return result

        if uri == 'rnz:root':
            result.append(Ref.album(name='Streams', uri='rnz:streams'))
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
            r, content = self.download(podcast_url)
            if r.status != 200:
                logging.error("failed to download %s", podcast_url)
                return None
            tree = ET.fromstring(content)
            #@_rnz_artist = Artist(name='RNZ')

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

    # def get_images(self, uris):
    #     logger.warn("RNZLibraryProvider::get_images(): %s", uris)
    #     # return content.images
    #     #result = super(RNZLibraryProvider, self).get_images(uris)
    #     #print(result)
    #     return {uri: content.images[uri] for uri in uris}

    def download(self, url):
        logger.info("RNZLibraryProvider::download() url:%s", url)
        return self.backend.download(url)

    def get_podcasts(self):
        if self.podcasts: return self.podcasts
        r, content = self.download(RNZLibraryProvider.PODCASTS_URI)
        if r.status != 200:
            logger.error("RNZ: Failed to download %s", RNZLibraryProvider.PODCASTS_URI)
            return []
        self.podcasts = json.loads(content)
        logger.info("RNZ: discovered %d podcasts", len(self.podcasts))
        return self.podcasts


class RNZLibraryProvider2(backend.LibraryProvider):
    podcasts = []
    match_podcast = re.compile(r'rnz:podcasts:\d+$')
    root_directory = Ref.directory(uri='rnz:root', name='RNZ')

    def __init__(self, backend):
        super(RNZLibraryProvider, self).__init__(backend=backend)
        logger.error("RNZLIbraryProvider::__init__()")

    def download(self, url):
        logger.info("RNZLibraryProvider::download() url:%s", url)
        return self.backend.download(url)

    def lookup(self, uri):
        logger.error('RNZLibraryProvider::lookup() uri:%s', uri)

        if not uri.startswith('rnz:'):
            logger.error("returning null")
            return None

        if uri.startswith('rnz:streams:'):
            return [streams[int(uri[uri.rfind(':') + 1:])]]

        if self.match_podcast.match(uri):
            index = int(uri[uri.rfind(':') + 1:])
            logger.info("returning podcast %i", index)
            artist = Artist(name='RNZ')
            podcast = self.get_podcasts[index]
            title = podcast['title']
            if title.startswith('RNZ: '): title = title[5:]
            return [Album(
                artists=[artist],
                images=[podcast['imageURL']],
                name=title,
            )]

        return []

    def browse(self, uri):
        logger.info('RNZLibraryProvider::browse() uri:%s', uri)

        result = []

        if uri == 'rnz:root':
            result.append(Ref.album(name='Streams', uri='rnz:streams'))
            result.append(Ref.directory(name='Podcasts', uri='rnz:podcasts'))
            result.append(Ref.track(name='Latest News Bulletin', uri='rnz:news'))
            return result

        if uri == 'rnz:streams':
            for n in range(len(streams)):
                result.append(Ref.track(
                    name=streams[n].name,
                    uri='rnz:streams:%i' % n
                ))
            return result




        else:
            return self.podcast_data.browse(uri)
        # elif uri == 'rnz:podcasts':
        #   n = 0
        #   for podcast in self.backend.podcast_data.get_podcasts():
        #     title = podcast['title']
        #     if title.startswith('RNZ: '): title = title[5:]
        #     result.append(Ref.directory(
        #       uri='rnz:podcasts:%i' % n,
        #       name=title,
        #     ))
        #     n += 1
        #   logger.info("added %i podcasts to result", n)
        # else:
        #   if self.match_podcast.match(uri):
        #     index = int(uri[uri.rfind(':') + 1:])
        #     #return PodcastRequest(self.backend).refs(uri,self.backend.podcasts_client.podcasts[index])
        #     return self.backend.podcast_data.get_podcast_refs()


        # for channel in self.backend.somafm.channels:
        #   result.append(Ref.track(
        #     uri='somafm:channel:/%s' % (channel),
        #     name=self.backend.somafm.channels[channel]['title']
        #   ))
        #
        # result.sort(key=lambda ref: ref.name.lower())
        return result

    def get_podcasts(self):
        if self.podcasts: return self.podcasts

        r, content = self.download(RNZLibraryProvider.PODCASTS_URI)
        if r.status != 200:
            logger.error("RNZ: Failed to download %s", RNZLibraryProvider.PODCASTS_URI)
            return None
        self.podcasts = json.loads(content)
        logger.info("RNZ: discovered %d podcasts", len(self.podcasts))
        return self.podcasts

    def browse(self, uri):
        logging.info("PodcastData::browse() uri:%s", uri)
        if uri == 'rnz:podcasts':
            return self.podcasts_refs()

        if self.match_podcast.match(uri):
            return self.podcast_item_refs(uri)
        return None

    def podcasts_refs(self):
        refs = []
        for podcast in self.get_podcasts():
            title = podcast['title']
            if title.startswith('RNZ: '): title = title[5:]
            refs.append(Ref.directory(
                uri='rnz:podcasts:%i' % len(refs),
                name=title
            ))
        return refs

    def podcast_item_refs(self, uri):
        index = int(uri[uri.rfind(':') + 1:])
        podcast = self.podcasts[index]
        podcast_uri = podcast['urls']
        r, content = self.download(podcast_uri)
        if r.status != 200:
            logging.error("failed to download %s", podcast_uri)
            return None
        tree = ET.fromstring(content)
        refs = []
        for item in tree.iter('item'):
            title = item.find('title').text.strip()
            refs.append(Ref.track(
                name=title,
                uri='%s:%i' % (uri, len(refs)),
            ))
        return refs
