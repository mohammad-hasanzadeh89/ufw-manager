import json
import re
from datetime import datetime, timedelta
from flask_cors import cross_origin
from flask import Blueprint, jsonify, request, escape
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import or_

from models.user import User, user_schema, users_schema
from utilities.db_manager import db, limiter
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
    if test and test.admin_privileges and not test.is_first:
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
    if test and test.admin_privileges and not test.is_first:
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


@user_api_blueprint.route("/add_user", methods=["POST"])
@jwt_required(fresh=True)
@cross_origin()
def add_user():
    remote_ip = request.remote_addr
    output = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_data = request.get_json()
    username = sanitizer(json_data.get("username", "")).lower()
    password = sanitizer(json_data.get("password", ""))
    admin = get_jwt_identity()
    test = User.query.filter_by(username=admin).first()
    if test and test.admin_privileges:
        if request.is_json:
            if len(username) < 4:
                add_log(
                    f"{remote_ip} as {test} tried to add new user with username: {username} and failed because of short username")
                return jsonify(
                    message="the username must be at least 4 char"), 400
            test_user = User.query.filter_by(username=username).first()
            if test_user:
                add_log(
                    f"{remote_ip} as {test} tried to add new user with username: {username} and failed because the user exists")
                return jsonify(
                    message="The username is not available."), 409
            else:
                if check_pass_is_strong(password):
                    new_user = User(username=username, password=password,
                                    admin_privileges=False, manager_privileges=False)
                    db.session.add(new_user)
                    db.session.commit()

                    add_log(
                        f"{remote_ip} as {test} add new user with username: {username} successfully")

                    return jsonify(
                        message=f"new user added with username: {username}"), 201
                else:
                    add_log(
                        f"{remote_ip} as {test} tried to add new user with username: {username} and failed because of weak passwrod")
                    return jsonify(
                        message="the password needs to be more than 8 char" +
                        "and must be upper case, lower case, digits and symbols like Test123!"), 400
        else:
            return jsonify("Bad Request.\nyou need to send parameters as json object"), 400
    else:
        add_log(
            f"{remote_ip} try to add new user with username: {username} as {test}")
        return jsonify(message="Unauthorized user"), 403


@user_api_blueprint.route("/signin", methods=["POST"])
@cross_origin()
@limiter.limit("3/minute;12/hour;100/day")
def signin():

    remote_ip = request.remote_addr
    if request.is_json:
        json_data = request.get_json()
        username = sanitizer(json_data.get("username", "")).lower()
        password = sanitizer(json_data.get("password", ""))

        user = User.query.filter_by(username=username).first()
        if user:
            is_password_right = user.verify_password(password)
            if is_password_right:
                if not user.is_deleted:
                    access_token = create_access_token(
                        fresh=True, identity=username,
                        expires_delta=timedelta(minutes=30))
                    add_log(f"{remote_ip} {user} logged in")
                    user = user_schema.dump(user)
                    return jsonify(
                        message="Login succeeded.",
                        access_token=access_token,
                        user=user)
                else:
                    add_log(
                        f"{remote_ip} tried to login as {username} and failed because of user deleted by admin")
                    return jsonify(message="Your admin has deleted your user. If you need more information, contact your admin."), 404
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


@user_api_blueprint.route("/delete_user", methods=["PUT"])
@jwt_required(fresh=True)
@cross_origin()
def delete_user():
    remote_ip = request.remote_addr
    json_data = request.get_json()
    username = sanitizer(json_data.get("username", "")).lower()
    admin = get_jwt_identity()
    test = User.query.filter_by(username=admin).first()
    if test and test.admin_privileges:
        if request.is_json:
            test_user = User.query.filter_by(username=username).first()
            if test_user:
                test_user.is_deleted = True
                db.session.add(test_user)
                db.session.commit()
                add_log(
                    f"{remote_ip} as {test} delete user with username: {username} successfully")

                return jsonify(
                    message=f"user with username: {username} deleted."), 200
            else:
                add_log(
                    f"{remote_ip} as {test} tried to delete user with username: {username} and failed because the user dose not exists")
                return jsonify(
                    message=f"user '{username}' dose not exists."), 404

        else:
            return jsonify("Bad Request.\nyou need to send parameters as json object"), 400
    else:
        add_log(
            f"{remote_ip} try to delete user with username: {username} as {test}")
        return jsonify(message="Unauthorized user"), 403


@user_api_blueprint.route("/change_password", methods=["POST"])
@jwt_required(fresh=True)
@cross_origin()
@limiter.limit("3/minute;12/hour;100/day")
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
                test.is_first = False
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
        if test and test.admin_privileges and not test.is_first:
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
