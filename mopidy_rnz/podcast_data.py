#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from mopidy.models import Ref

import logging,json,re

logger = logging.getLogger(__name__)

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


class PodcastData(object):
  PODCASTS_URI = 'https://h1.danbrough.org/data/podcastinfo_v1.json'
  podcasts = []

  def __init__(self,request_method):
    self.download = request_method
    self.match_podcast = re.compile(r'rnz:podcasts:\d+$')


  # def get_images(self,uris):
  #   logging.warn("get_images(): %s",uris[0])
  #   index = int(uris[0].split(':')[2])
  #
  #   logging.warn("podcast: %s",self.get_podcasts()[index])
  #   image = self.get_podcasts()[index]['imageURL']
  #   return [image for n in self.get_podcasts()]




#
#  Retrieve pre-generated RNZ podcast metadata
#
#
# class PodcastRequest(object):
#   podcast = {}
#
#   def __init__(self, backend):
#     super(PodcastRequest, self).__init__()
#     self.backend = backend
#
#   def refs(self, podcast_uri,podcast):
#     logger.info("PodcastRequest::refs() podcast:%s", podcast)
#
#
#     url = podcast['urls']
#     try:
#       r,content = self.request_method(url)
#       logger.debug("Get %s : %i", url, r.status)
#
#       if r.status is not 200:
#         logger.error(
#           "RNZ: %s is not reachable [http code:%i]",
#           url, r.status)
#         return None
#
#       tree = ET.fromstring(content)
#       items = []
#       for item in tree.iter('item'):
#         title = item.find('title').text.strip()
#         items.append(Ref.track(
#           name = title,
#           uri = '%s:%i' % (podcast_uri, len(items)),
#         ))
#       return items
#
#
#     except Exception as e:
#       logger.error("RNZ exception: %s", e)
#       return None
#
#     return None
