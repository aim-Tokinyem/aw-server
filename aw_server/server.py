import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

from functools import wraps
from flask_jwt import JWTError


import aw_datastore
import flask.json.provider
from aw_datastore import Datastore
from flask import (
    Blueprint,
    Flask,
    current_app,
    send_from_directory,
    request,
    jsonify,
)
from flask_cors import CORS

from . import rest
from .api import ServerAPI
from .custom_static import get_custom_static_blueprint
from .log import FlaskLogHandler
from .generate import TokenGenerator

logger = logging.getLogger(__name__)

app_folder = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(app_folder, "static")

root = Blueprint("root", __name__, url_prefix="/")


class AWFlask(Flask):
    def __init__(
        self,
        host: str,
        testing: bool,
        storage_method=None,
        cors_origins=[],
        custom_static=dict(),
        static_folder=static_folder,
        static_url_path="",
    ):
        name = "aw-server"
        self.json_provider_class = CustomJSONProvider
        # only prettyprint JSON if testing (due to perf)
        self.json_provider_class.compact = not testing

        # Initialize Flask
        Flask.__init__(
            self,
            name,
            static_folder=static_folder,
            static_url_path=static_url_path,
        )
        self.config["HOST"] = host  # needed for host-header check
       # with self.app_context():
        self._config_cors(cors_origins, testing)

        # Initialize datastore and API
        if storage_method is None:
            storage_method = aw_datastore.get_storage_methods()["memory"]
        db = Datastore(storage_method, testing=testing)
        self.api = ServerAPI(db=db, testing=testing)

        self.register_blueprint(root)
        self.register_blueprint(rest.blueprint)
        self.register_blueprint(get_custom_static_blueprint(custom_static))

    def _config_cors(self, cors_origins: List[str], testing: bool):
        if cors_origins:
            logger.warning(
                "Running with additional allowed CORS origins specified through config "
                "or CLI argument (could be a security risk): {}".format(cors_origins)
            )

        if testing:
            # Used for development of aw-webui
            cors_origins.append("http://127.0.0.1:27180/*")

        # TODO: This could probably be more specific
        #       See https://github.com/ActivityWatch/aw-server/pull/43#issuecomment-386888769
        cors_origins.append("moz-extension://*")

        # See: https://flask-cors.readthedocs.org/en/latest/
        CORS(self, resources={r"/api/*": {"origins": cors_origins}})

class CustomJSONProvider(flask.json.provider.DefaultJSONProvider):
    # encoding/decoding of datetime as iso8601 strings
    # encoding of timedelta as second floats
    def default(self, obj, *args, **kwargs):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, timedelta):
                return obj.total_seconds()
        except TypeError:
            pass
        return super().default(obj)


@root.route("/")
def static_root():
    return current_app.send_static_file("index.html")

token_generator = TokenGenerator()
@root.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Handle the POST request data and perform registration
        data = request.get_json()
        # Perform registration logic here...
        # For example, you can extract the hostname from the JSON data
        hostname = data.get("hostname")
        if hostname:
            token = token_generator.generate_token(hostname)
            token_str = token.decode("utf-8")
            response_data = {"message": "Registration successful!", "hostname": hostname,"token":token_str}
            return jsonify(response_data), 200
        else:
            response_data = {"error": "Invalid request data"}
            return jsonify(response_data), 400
        
    else:
        return "Hello"


@root.route("/css/<path:path>")
def static_css(path):
    return send_from_directory(static_folder + "/css", path)


@root.route("/js/<path:path>")
def static_js(path):
    return send_from_directory(static_folder + "/js", path)


def _config_cors(cors_origins: List[str], testing: bool):
    if cors_origins:
        logger.warning(
            "Running with additional allowed CORS origins specified through config "
            "or CLI argument (could be a security risk): {}".format(cors_origins)
        )

    if testing:
        # Used for development of aw-webui
        cors_origins.append("http://127.0.0.1:27180/*")

    # TODO: This could probably be more specific
    #       See https://github.com/ActivityWatch/aw-server/pull/43#issuecomment-386888769
    cors_origins.append("moz-extension://*")

    # See: https://flask-cors.readthedocs.org/en/latest/
    CORS(current_app, resources={r"/api/*": {"origins": cors_origins}})


# Only to be called from aw_server.main function!
def _start(
    storage_method,
    host: str,
    port: int,
    testing: bool = False,
    cors_origins: List[str] = [],
    custom_static: Dict[str, str] = dict(),
):
    app = AWFlask(
        host,
        testing=testing,
        storage_method=storage_method,
        cors_origins=cors_origins,
        custom_static=custom_static,
    )
    # Register the authentication handler

    try:
        app.run(
            debug=testing,
            host=host,
            port=port,
            request_handler=FlaskLogHandler,
            use_reloader=False,
            threaded=True,
        )
    except OSError as e:
        logger.exception(e)
        raise e
