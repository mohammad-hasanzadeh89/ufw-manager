
import os.path as path
import secrets
from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from routes.ufw_manager_routes import ufw_manager_blueprint, update_service_table
from routes.user_routes import user_api_blueprint, create_admin
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
# app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(48) TODO uncomment it and comment next line
app.config["JWT_SECRET_KEY"] = "secrets.token_urlsafe(48)"
app.config['CORS_HEADERS'] = 'Content-Type'

db_init_app(app)
db_create_tables(app)
ma_init_app(app)
bcrypt_init_app(app)
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
    create_admin()
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
@cross_origin()
def route_not_found(error):
    return jsonify('This route does not exist'), 404


@jwt.expired_token_loader
def expire_token(header, payload):
    return jsonify(msg="Token has expired"), 401


if __name__ == "__main__":
    print("*****Use this instead*****\nsudo venv/bin/gunicorn -b=127.0.0.1:5000 app:app")
