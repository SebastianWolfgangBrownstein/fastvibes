from __future__ import unicode_literals
import os
import json

from flask import (
    Blueprint, current_app, request, Response, send_from_directory
)

bp = Blueprint('download', __name__, url_prefix='/download')

@bp.post('/audio')
def download():
    print('Attempting Download...')
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        return Response(json.dump({'Error': 'Content-Type not supported'}), status=400, mimetype='application/json')
    else:
        body = request.json
        filename = body['filename']
        mediapath = os.path.join(current_app.root_path, 'media')
        return send_from_directory(mediapath, filename, as_attachment=True)
        