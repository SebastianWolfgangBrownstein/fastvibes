from flask import (
    Blueprint, request, jsonify
)

bp = Blueprint('query', __name__, url_prefix='/query')

@bp.get('/metadata')
def metadata():
    url = request.args.get('url')

    data = {
        'url' : url,
        'title': 'Fast Title - Good Artist',
        'thumb': 'songthumb.png'
    }
    return jsonify(data)