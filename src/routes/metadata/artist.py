from __future__ import unicode_literals
from flask import (
    Blueprint, request, Response, jsonify
)
import json
from ...lib.errors.api_errors import (
    BadRequestError
)
from ...services.lastfm import LastFM
from ...services.musicbrainz import Brainz

bp = Blueprint('artist', __name__, url_prefix='/artist')


@bp.get('/')
async def artist():
    try:
        args = request.args

        artist = args.get('artist')
        mode = args.get('mode')
        if artist is None:
            raise BadRequestError('artist parameter is undefined')

        lastFMData = await LastFM.getArtistData(artist)
        brainzData = await Brainz.findArtistByName(artist, populate=True)
        # eventually merge all data sources here
        return jsonify(brainzData)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/bio')
async def artist_bio():
    try:
        args = request.args
        artist = args.get('artist')

        if artist is None:
            raise BadRequestError('artist parameter is undefined')

        data = await LastFM.getArtistBio(artist)

        return jsonify(data)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/similar')
async def similar_artists():
    try:
        args = request.args
        artist = args.get('artist')
        if artist is None:
            raise BadRequestError('artist parameter is undefined')

        data = await LastFM.getSimilarArtists(artist)
        return jsonify(data)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/tags')
async def artist_tags():
    try:
        args = request.args
        artist = args.get('artist')
        if artist is None:
            raise BadRequestError('artist parameter is undefined')

        data = await LastFM.getArtistTags(artist)
        return jsonify(data)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/links')
async def artist_links():
    try:
        args = request.args
        artist = args.get('artist')
        brainzData = await Brainz.findArtistByName(artist, populate=True)
        parsedLinks = Brainz.formatArtistLinks(brainzData)
        responsePayload = {
            'artist': artist,
            'artistLinks': parsedLinks
        }
        return jsonify(responsePayload)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')


@bp.get('/<mbid>')
async def artist_by_mbid(mbid):
    try:
        artist = await Brainz.findArtist(mbid)

        return jsonify(artist)
    except BadRequestError as e:
        print(f'BadRequestError: {e}')
        return Response(f"BadRequestError: {e}", status=400, mimetype='application/json')
    except Exception as e:
        print(f'UncaughtException: {e}')
        return Response(json.dump({'Error': 'Internal Server Error'}), status=500, mimetype='application/json')
