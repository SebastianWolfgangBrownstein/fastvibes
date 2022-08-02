from __future__ import unicode_literals
from flask import (
    Blueprint, request, Response, jsonify
)
import json
import yt_dlp

from .services import (deezer, lastfm)
from .util.parsers import parseTrackAndArtist

bp = Blueprint('metadata', __name__, url_prefix='/meta')


@bp.get('/yt')
async def metadata():
    url = request.args.get('url')

    if url is None:
        return Response(json.dump({'Error': 'No URL Query Provided'}), status=400, mimetype='application/json')

    data = await getVideoInfo(url)
    # data = rawData.get_json()
    if data is None:
        return Response(json.dump({'Error': 'Not Found'}), status=404, mimetype='application/json')
    else:
        trackAndArtist = parseTrackAndArtist(
            data.get('title'), data.get('channel'))

        deezerData = await deezer.getDeezerData(trackAndArtist['artist'], trackAndArtist['track'])
        artistBio = await lastfm.getArtistBio(trackAndArtist['artist'])
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
            'releaseDate': deezerData and deezerData.get('release_date'),
            'artistThumb': deezerData and deezerData.get('artist_thumb'),
            'artistBio': artistBio,
            'track': trackAndArtist['track'],
            'artist': trackAndArtist['artist'],
            'album': data.get('album')

        }
        return jsonify(payload)


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


@bp.get('/artist/<mbid>')
async def artist_by_mbid(mbid):
    return f"/artist/{mbid}"


@bp.get('/artist')
async def artist():
    return '/meta/artist'


@bp.get('/track/isrc/<isrc>')
async def track_by_isrc(isrc):
    return f"/track/isrc/{isrc}"


@bp.get('/track/<mbid>')
async def track_by_mbid(mbid):
    return f"/track/{mbid}"


@bp.get('/track')
async def track():
    return '/track'
