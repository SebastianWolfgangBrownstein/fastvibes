from __future__ import unicode_literals
from flask import (
    Blueprint, request, Response, jsonify
)
import json
import yt_dlp

from ...services.lastfm import LastFM
from ...services.deezer import Deezer
from ...services.musicbrainz import Brainz

from ...lib.parsers.parseTrackAndArtist import parseTrackAndArtist
from ...lib.errors.api_errors import (
    BadRequestError,
    NotFoundError
)

from . import (artist, track)
bp = Blueprint('metadata', __name__, url_prefix='/meta')
bp.register_blueprint(artist.bp)
bp.register_blueprint(track.bp)


@bp.get('/yt')
async def metadata():
    url = request.args.get('url')
    try:
        if url is None:
            return Response(json.dump({'Error': 'No URL Query Provided'}), status=400, mimetype='application/json')

        data = await getVideoInfo(url)

        if data is None:
            raise NotFoundError('Video not found')
        else:
            trackAndArtist = parseTrackAndArtist(
                data.get('title'), data.get('channel'))
            deezerData = await Deezer.getTrackData(trackAndArtist['artist'], trackAndArtist['track'])
            recordingData = await Brainz.ISRC(deezerData.get('isrc'), populate=True)
            artistBio = await LastFM.getArtistBio(trackAndArtist['artist'])

            payload = {
                'url': url,
                'fileId': data.get('id'),
                'title': data.get('title'),
                'channel': data.get('channel'),
                'creator': data.get('creator'),
                'description': data.get('description'),
                'thumb': data.get('thumbnail'),
                'duration': data.get('duration'),
                'durationString': data.get('duration_string'),
                'abr': data.get('abr'),
                'asr': data.get('asr'),
                'bpm': deezerData and deezerData.get('bpm') or 0,
                'isrc': deezerData and deezerData.get('isrc'),
                'dzid': deezerData and deezerData.get('dzid'),
                'recordingMBID': recordingData and recordingData.get('recording_mbid'),
                'releaseDate': deezerData and deezerData.get('release_date'),
                'artistThumb': deezerData and deezerData.get('artist_thumb'),
                'artistBio': artistBio and artistBio.get('bio'),
                'artistMBID': recordingData and recordingData.get('artist_mbid'),
                'track': trackAndArtist['track'],
                'artist': trackAndArtist['artist'],
                'album': data.get('album')

            }
            return jsonify(payload)
    except NotFoundError as e:
        print(f'NotFoundError: {e}')
        return Response(f"NotFoundError: {e}", status=404, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response('Internal Server Error', status=500, mimetype='application/json')


async def getVideoInfo(url):
    info = await fetchVideoInfo(url)
    if info is None:
        pass
    else:
        return info


async def fetchVideoInfo(url):
    ydl_opts = {
        'format': 'bestaudio/best'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=False)

        if info is None:
            print('No Data')
            return None
        else:
            print('Data Found!')
            # return json.dumps(ydl.sanitize_info(info))
            return ydl.sanitize_info(info)


# @bp.get('/track/isrc/<isrc>')
# async def track_by_isrc(isrc):
#     return f"/track/isrc/{isrc}"


# @bp.get('/track/<mbid>')
# async def track_by_mbid(mbid):
#     return f"/track/{mbid}"


# @bp.get('/track')
# async def track():
#     return '/track'
