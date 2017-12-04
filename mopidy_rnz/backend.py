from __future__ import unicode_literals

import logging
import pykka
import re
import httplib2
import json
import os

from mopidy import backend
from mopidy.models import Ref, Artist, Album

logger = logging.getLogger(__name__)

from .podcast_data import PodcastData

httplib2.debuglevel = 5

class RNZBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(RNZBackend, self).__init__()
        self.library = RNZLibraryProvider(backend=self)
        self.uri_schemes = ['rnz']

        cache_dir = config['rnz']['cache_dir']
        cache_dir = os.path.expanduser(cache_dir)
        logging.info("cache_dir: %s",cache_dir)
        self.http_cache = httplib2.Http(cache_dir)

        self.podcast_data = PodcastData(self.download)
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


from .content import streams


class RNZLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri='rnz:root', name='RNZ')
    PODCASTS_URI = 'https://h1.danbrough.org/data/podcastinfo_v1.json'
    podcasts = []

    def __init__(self, backend):
        super(RNZLibraryProvider, self).__init__(backend)
        self.download = backend.download
        self.match_podcast = re.compile(r'rnz:podcasts:\d+$')

    def lookup(self, uri):
        logger.warn('RNZLibraryProvider::lookup() uri:%s', uri)

        if not uri.startswith('rnz:'):
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

    # def get_images(self, uris):
    #   logger.warn("RNZLibraryProvider::get_images(): %s", uris)
    #   if uris[0].startswith('rnz:podcasts'):
    #     return self.backend.podcast_data.get_images(uris)
    #
    #   return super(RNZLibraryProvider, self).get_images(uris)

    def browse(self, uri):
        logger.warn('RNZLibraryProvider::browse() uri:%s', uri)

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

        r, content = self.download(PodcastData.PODCASTS_URI)
        if r.status != 200:
            logger.error("RNZ: Failed to download %s", PodcastData.PODCASTS_URI)
            return None
        self.podcasts = json.loads(content)
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

