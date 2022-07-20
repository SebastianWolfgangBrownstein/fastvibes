from __future__ import unicode_literals
import os
import json

from flask import (
    Blueprint, current_app, request, Response, send_from_directory
)

bp = Blueprint('download', __name__, url_prefix='/download')

@bp.get('/audio')
def download():
    print('Attempting Download...')
    args = request.args.to_dict()
    fileId = args.get("fileId")
    fileFormat = args.get("fileFormat")
    filename = f"{fileId}.{fileFormat}"
    # content_type = request.headers.get('Content-Type')
    if (fileId is None or fileFormat is None):
        return Response(json.dump({'Error': 'Invalid Download Params'}), status=400, mimetype='application/json')
    else:
        # body = request.json
        # filename = body['filename']
        mediapath = os.path.join(current_app.root_path, 'media')
        return send_from_directory(mediapath, filename, as_attachment=True)
        