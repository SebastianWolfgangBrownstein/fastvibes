import os
from flask import Flask
# from flask_cors import CORS


def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY")
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .routes.metadata import metadata
    app.register_blueprint(metadata.bp)

    from . import convert
    app.register_blueprint(convert.bp)

    from . import download
    app.register_blueprint(download.bp)

    from . import test
    app.register_blueprint(test.bp)

    @app.get("/")
    def index():
        return "FasterVibes API"

    return app


app = create_app()
