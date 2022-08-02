from flask import (
    Blueprint, request, Response, jsonify
)
from .services import deezer

bp = Blueprint('test', __name__, url_prefix='/test')


@bp.get('/deezer')
async def deezer_data():
    artist = request.args.get('artist')
    track = request.args.get('track')

    deezerData = await deezer.getDeezerData(artist, track)
    # trackId = await deezer.search(artist, track)

    # trackData = await deezer.lookupTrack(trackId)

    # payload = {
    #     'track': track,
    #     'artist': artist,
    #     'dzid': trackId,
    #     'isrc': trackData.get('isrc'),
    #     'release_date': trackData.get('release_date'),
    #     'artist_thumb': trackData.get('artist_thumb'),
    #     'bpm': trackData.get('bpm')
    # }

    return jsonify(deezerData)
