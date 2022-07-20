from __future__ import unicode_literals
from flask import (
    Blueprint, request, Response, jsonify
)
import json
import yt_dlp


bp = Blueprint('metadata', __name__, url_prefix='/meta')

@bp.get('/query')
async def metadata():
    url = request.args.get('url')

    if url is None:
        return Response(json.dump({'Error': 'No URL Query Provided'}), status=400, mimetype='application/json')

    data = await getVideoInfo(url)
    # data = rawData.get_json()
    if data is None:
        return Response(json.dump({ 'Error': 'Not Found' }), status=404, mimetype='application/json') 
    else:
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
            'asr': data.get('asr')
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
        info = ydl.extract_info(url, download = False)

        if info is None:
            print('No Data')
            return None
        else:
            print('Data Found!')
            # return json.dumps(ydl.sanitize_info(info))
            return ydl.sanitize_info(info)