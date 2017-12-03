from __future__ import unicode_literals

import logging
from mopidy import backend
from mopidy.models import Album, Artist, Ref, Track
import pykka
import mopidy_rnz

logger = logging.getLogger(__name__)


class RNZBackend(pykka.ThreadingActor, backend.Backend):

  def __init__(self, config, audio):
    super(RNZBackend, self).__init__()
    self.library = RNZLibraryProvider(backend=self)
    self.uri_schemes = ['rnz']

from .content import streams


class RNZLibraryProvider(backend.LibraryProvider):

  root_directory = Ref.directory(uri='rnz:root', name='RNZ')

  def lookup(self, uri):
    logger.warn('RNZLibraryProvider::lookup() uri:%s',uri)

    if not uri.startswith('rnz:'):
      return None

    if uri.startswith('rnz:streams:'):

      return [streams[int(uri[uri.rfind(':')+1:])]]


    return []

  def browse(self, uri):
    logger.warn('RNZLibraryProvider::browse() uri:%s',uri)

    result = []


    if uri == 'rnz:root':
      result.append(Ref.album(name='Streams',uri='rnz:streams'))
      result.append(Ref.album(name='Podcasts',uri='rnz:podcasts'))
    elif uri == 'rnz:streams':
      for n in range(len(streams)):
        result.append(Ref.track(
          name = streams[n].name,
          uri = 'rnz:streams:%i'%n
        ))


    # for channel in self.backend.somafm.channels:
    #   result.append(Ref.track(
    #     uri='somafm:channel:/%s' % (channel),
    #     name=self.backend.somafm.channels[channel]['title']
    #   ))
    #
    # result.sort(key=lambda ref: ref.name.lower())
    return result
