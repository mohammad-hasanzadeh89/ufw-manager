import json
import re
from datetime import datetime, timedelta
from flask_cors import cross_origin
from flask import Blueprint, jsonify, request, escape
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import or_

from models.user import User, user_schema, users_schema
from utilities.db_manager import db
from utilities.sanitizer import sanitizer
from utilities.logger import add_log

user_api_blueprint = Blueprint(
    'user_api_blueprint', __name__)


@user_api_blueprint.route("/get_all_user", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_all_user():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges:
        users = User.query.paginate(
            page, per_page, error_out=False)
        total = users.total
        users = users.items
        result = users_schema.dump(users)
        output = {
            "result": result,
            "total": total,
            "date": now
        }

        log_msg = f"{remote_ip} get all user records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all user records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@user_api_blueprint.route("/get_users", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_users():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5
    id = sanitizer(request.args.get("id", "0"))
    id = int(id) if id is not None and id.isnumeric() else 0
    query_username = sanitizer(request.args.get("username", "undefined"))
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges:
        users = User.query.filter(
            or_(User.id == id,
                User.username.like(f"%{query_username}%"))).paginate(
            page, per_page, error_out=False)
        total = users.total
        users = users.items
        result = users_schema.dump(users)
        output = {
            "result": result,
            "total": total,
            "date": now
        }
        if total == 0:
            status_code = 404
        log_msg = f"{remote_ip} get all user records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all user records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@user_api_blueprint.route("/get_user_privileges", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_user_privileges():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test:
        result = {
            "isAdmin": test.admin_privileges,
            "isManager": test.manager_privileges
        }
        output = {
            "result": result,
            "date": now
        }

        log_msg = f"{remote_ip} get {test} privileges records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get {test} privileges records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@user_api_blueprint.route("/signup", methods=["POST"])
@cross_origin()
def signup():
    remote_ip = request.remote_addr
    if request.is_json:
        json_data = request.get_json()
        username = sanitizer(json_data.get("username", ""))
        password = sanitizer(json_data.get("password", ""))

        test = User.query.filter_by(username=username).first()
        if test:
            add_log(
                f"{remote_ip} tried to sign up with {username} and failed because the user exists")
            return jsonify(
                message="The username is not available."), 409
        else:
            if check_pass_is_strong(password):
                new_user = User(username=username, password=password,
                                admin_privileges=False, manager_privileges=False)
                db.session.add(new_user)
                db.session.commit()

                add_log(
                    f"{remote_ip} signup with {username} successfully")

                return jsonify(message="Your username registered," +
                               " contact your system administrator to get your access"), 201
            else:
                add_log(
                    f"{remote_ip} tried to signup with {username} and failed because of weak passwrod")
            return jsonify(
                message="the password needs to be more than 8 char" +
                "and must be upper case, lower case, digits and symbols like Test123!"), 400
    else:
        return jsonify("Bad Request.\nyou need to send parameters as json object"), 400


@user_api_blueprint.route("/signin", methods=["POST"])
@cross_origin()
def signin():

    remote_ip = request.remote_addr
    if request.is_json:
        json_data = request.get_json()
        username = sanitizer(json_data.get("username", ""))
        password = sanitizer(json_data.get("password", ""))

        user = User.query.filter_by(username=username).first()
        if user:
            is_password_right = user.verify_password(password)
            if is_password_right:
                access_token = create_access_token(
                    fresh=True, identity=username,
                    expires_delta=timedelta(minutes=30))
                add_log(f"{remote_ip} {user} logged in")
                return jsonify(message="Login succeeded.", access_token=access_token)
            else:
                add_log(
                    f"{remote_ip} tried to login as {username} and failed because of wrong password")
                return jsonify(message="Wrong username or password!"), 403
        else:
            add_log(
                f"{remote_ip} tried to login as {username} and failed because of wrong username")
            return jsonify(message="Wrong username or password!"), 403
    else:
        return jsonify("Bad Request.\nyou need to send parameters as json object"), 400


@user_api_blueprint.route("/change_password", methods=["POST"])
@jwt_required(fresh=True)
@cross_origin()
def change_password():
    remote_ip = request.remote_addr

    if request.is_json:
        json_data = request.get_json()
        username = get_jwt_identity()
        current_password = sanitizer(json_data.get(
            "current_password", ""))
        new_password = sanitizer(json_data.get("new_password", ""))
        confirm_new_password = sanitizer(json_data.get(
            "confirm_new_password", ""))

        if (current_password != "" and check_pass_is_strong(new_password) and
                check_pass_is_strong(confirm_new_password)
                and new_password == confirm_new_password
                and current_password != new_password):
            test = User.query.filter_by(username=username).first()
            if test and test.verify_password(current_password):
                test.set_password(new_password)
                db.session.commit()
                add_log(f"{remote_ip} as {test} change his/hers password")
                return jsonify(message="Your password changed successfully."), 200
            else:
                add_log(
                    f"{remote_ip} tried as {test} to change his/hers password and failed because of wrong password")
                return jsonify(message="Unauthorized user. wrong password"), 403
        else:
            add_log(
                f"{remote_ip} tried as {username} to change his/hers password and failed because of Bad request parameters")
            return jsonify(message="Bad request. weak new password or something similar"), 400
    else:
        return jsonify("Bad Request.\nyou need to send parameters as json object"), 400


@ user_api_blueprint.route("/grant_authorization", methods=["POST"])
@ jwt_required(fresh=True)
@cross_origin()
def grant_authorization():
    remote_ip = request.remote_addr
    if request.is_json:
        json_data = request.get_json()
        output = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin = get_jwt_identity()
        test = User.query.filter_by(username=admin).first()
        username = sanitizer(json_data.get("username", ""))
        if test and test.admin_privileges:
            if username is None:
                add_log(
                    f"{remote_ip} as admin try to grant manager privileges but failed because of not providing username")
                return jsonify(message="Bad request."), 400
            user = User.query.filter_by(username=username).first()
            if user:
                user.manager_privileges = True
                db.session.add(user)
                db.session.commit()
                output.append(f"{user} authorized with manager privileges")
                output.append("date: " + now)

                add_log(
                    f"{remote_ip} as admin grant manager privileges to {user}")

                return jsonify(message=output)
            else:
                output.append(f"user '{username}' does not exist")
                output.append("date: " + now)

                add_log(
                    f"{remote_ip} as admin try to grant manager privileges to {username}")

                return jsonify(message=output), 404
        else:
            add_log(
                f"{remote_ip} try to grant manager privileges to {username} as {admin}")
            return jsonify(message="Unauthorized user"), 403
    else:
        return jsonify("Bad Request.\nyou need to send parameters as json object"), 400


def create_admin():
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        new_user = User(username="admin", password="admin",
                        admin_privileges=True, manager_privileges=True)
        add_log(f"admin created")
        db.session.add(new_user)
        db.session.commit()


def check_pass_is_strong(pwd):
    if pwd == None or len(pwd) < 8:
        return False
    else:
        regex = ("^(?=.*[a-z])(?=." +
                 "*[A-Z])(?=.*\\d)" +
                 "(?=.*[-+_!@#$%^&*., ?]).+$")
        compiled_regex = re.compile(regex)
        if re.search(compiled_regex, pwd):
            return True
        else:
            return False


def bool_checker(str_param):
    return str_param and str_param.isdigit() and bool(int(str_param))
