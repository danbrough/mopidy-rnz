from mopidy.models import Album, Artist, Ref, Track
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

_news_album = Album(
  artists = [_rnz_artist],
  images = ['http://www.radionz.co.nz/brand-images/rnz-international.jpg'],
  name = 'RNZ International',
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
  uri = 'http://radionz-ice.streamguys.com/national_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _national_album,
  name = 'National Radio High Quality',
  uri = 'http://radionz-ice.streamguys.com/National_aac128',
))


streams.append(Track(
  artists = [_rnz_artist],
  album = _national_album,
  name = 'National Radio Low Quality',
  uri = 'http://radionz-ice.streamguys.com/national',
))


streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM',
  uri = 'http://radionz-ice.streamguys.com/concert_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM High Quality',
  uri = 'http://radionz-ice.streamguys.com/Concert_aac128',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _concert_album,
  name = 'Concert FM Low Quality',
  uri = 'http://radionz-ice.streamguys.com/concert',
))



streams.append(Track(
  artists = [_rnz_artist],
  album = _international_album,
  name = 'RNZ International',
  uri = 'http://radionz-ice.streamguys.com/international_aac64',
))

streams.append(Track(
  artists = [_rnz_artist],
  album = _parliament_album,
  name = 'Parliament Live Stream',
  uri = 'http://radionz-ice.streamguys.com/parliament',
))


# album = Album(
      #   artists = [_rnz_artist],
      #   images = ['http://www.radionz.co.nz/brand-images/rnz-national.jpg'],
      #   name = 'RNZ National',
      # )
      #
      # track = Track(
      #   artists=[artist],
      #   album = album,
      #   name=  'RNZ National: ' + uri[uri.rfind(':')+1:],
      #   uri = 'http://radionz-ice.streamguys.com/National_aac128',
      # )