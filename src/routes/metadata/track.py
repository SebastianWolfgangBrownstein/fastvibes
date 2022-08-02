from __future__ import unicode_literals
from flask import (
    Blueprint, request, Response, jsonify
)
import json
from ...lib.errors.api_errors import (
    BadRequestError,
    NotFoundError
)

from ...services.deezer import Deezer
from ...services.musicbrainz import Brainz

bp = Blueprint('track', __name__, url_prefix='/track')


@bp.get('/')
async def track():
    try:
        args = request.args
        artist = args.get('artist')
        track = args.get('track')
        if artist is None:
            raise BadRequestError('artist parameter is undefined')

        if track is None:
            raise BadRequestError('track parameter is undefined')

        deezerData = await Deezer.getTrackData(artist, track)
        if deezerData is None:
            raise NotFoundError('track not found')

        isrc = deezerData.get('isrc')

        brainzData = await Brainz.ISRC(isrc, populate=True)

        return jsonify(brainzData)
    except BadRequestError as e:
        print(f'BadRequest: {e}')
        return Response(f"BadRequest: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/isrc/<isrc>')
async def track_by_isrc(isrc):
    try:
        brainzData = await Brainz.ISRC(isrc, populate=True)
        return jsonify(brainzData)
    except BadRequestError as e:
        print(f'BadRequest: {e}')
        return Response(f"BadRequest: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/<mbid>')
async def track_by_mbid(mbid):
    return f"/track/{mbid}"
