from mopidy.models import Album, Artist, Ref, Track,Image
import logging

logger = logging.getLogger(__name__)


_rnz_artist = Artist(name='RNZ')

_national_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-national.jpg'],
  name = 'RNZ National',
)

_concert_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-concert.jpg'],
  name = 'RNZ Concert',
)

_news_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-news.jpg'],
  name = 'RNZ News',
)

_parliament_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-parliament.jpg'],
  name = 'RNZ Parliament',
)

_international_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-international.jpg'],
  name = 'RNZ International',
)

streams = []

streams.append(Track(
  artists = [_rnz_artist],
  album = _national_album,
  name = 'National Radio',
  bitrate = 64,
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/national_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _national_album,
  name = 'National Radio High Quality',
  track_no = len(streams),
  bitrate = 128,
  uri = 'http://radionz-ice.streamguys.com/National_aac128',
))


streams.append(Track(
  artists = [_rnz_artist],
  album = _national_album,
  track_no = len(streams),
  name = 'National Radio Low Quality',
  uri = 'http://radionz-ice.streamguys.com/national',
))


streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM',
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/concert_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM High Quality',
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/Concert_aac128',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM Low Quality',
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/concert',
))


streams.append(Track(
  artists = [_rnz_artist],
  album = _international_album,
  name = 'RNZ International',
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/international_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _parliament_album,
  name = 'Parliament Live Stream',
  track_no = len(streams),
  uri = 'http://radionz-ice.streamguys.com/parliament',
))

news_track = Track(
  artists = [_rnz_artist],
  album = _news_album,
  name = 'Latest News Bulletin',
  track_no = 1,
)





