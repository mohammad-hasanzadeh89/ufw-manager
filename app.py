import os.path as path
from datetime import datetime
import secrets
from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from routes.ufw_manager_routes import ufw_manager_blueprint, update_service_table
from routes.user_routes import user_api_blueprint
from utilities.db_manager import *

app = Flask(__name__)
cors = CORS(app)
base_dir = path.abspath(path.dirname(__file__))
resource_dir = path.join(base_dir, "resource")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + \
    path.join(resource_dir, "data_base.db")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "json"]
app.config["JWT_COOKIE_SECURE"] = False
is_static_secret_key = config_data.get("is_static_secret_key")
static_secret_key = config_data.get("static_secret_key")
if (is_static_secret_key is not None and is_static_secret_key
    ) and (static_secret_key is not None):
    app.config["JWT_SECRET_KEY"] = static_secret_key
else:
    app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
app.config['CORS_HEADERS'] = 'Content-Type'

db_init_app(app)
db_create_tables(app)
ma_init_app(app)
bcrypt_init_app(app)
limiter_init_app(app)
jwt = JWTManager(app)

app.register_blueprint(ufw_manager_blueprint, url_prefix="/api")
app.register_blueprint(user_api_blueprint, url_prefix="/api")

SWAGGER_URL = '/docs'
API_URL = '/docs.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.before_first_request
def before_first_request():
    update_service_table()


@app.route("/")
def index():
    return render_template('base.html')


@app.route("/docs.json", methods=['GET'])
def swagger_api_docs_yml():
    with open('swagger.json') as fd:
        json_data = json.load(fd)

    return jsonify(json_data)


@ app.errorhandler(404)
def route_not_found(error):
    return jsonify('This route does not exist'), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    msg = str(e).replace("429 ", "")
    return jsonify(message=msg,
                   result=msg,
                   date=datetime.now().strftime(
                       "%Y-%m-%d %H:%M:%S")), 429


@jwt.expired_token_loader
def expire_token(header, payload):
    return jsonify(msg="Token has expired"), 401


if __name__ == "__main__":
    print("*****Use this instead*****\nsudo venv/bin/gunicorn -b=0.0.0.0:8080 app:app")
