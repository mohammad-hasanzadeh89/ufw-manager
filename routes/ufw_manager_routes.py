from models.route import Route
import subprocess
from ipaddress import ip_address, IPv4Address
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_, func

from models.status import Status, status_schema, statuses_schema
from models.rule import Rule, rule_schema, rules_schema
from models.deleted_rule import DeletedRule, deleted_rule_schema, deleted_rules_schema
from models.route import Route, route_schema, routes_schema
from models.deleted_route import DeletedRoute, deleted_route_schema, deleted_routes_schema
from models.user import User, user_schema
from models.service import Service, service_schema, services_schema
from utilities.db_manager import db
from utilities.sanitizer import sanitizer
from utilities.logger import add_log

ufw_manager_blueprint = Blueprint(
    'ufw_manager_blueprint', __name__)
rule_actions = ["allow", "deny", "reject", "limit"]
rule_protocols = ["tcp/udp", "tcp", "udp", "ah",
                  "esp", "gre", "ipv6", "igmp"]


@ufw_manager_blueprint.route("/get_services", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_services():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        services = Service.query.all()
        if len(services) > 0:
            services = services_schema.dump(services)
            services = [service["service_name"] for service in services]
            temp_list = sorted({*services})
            result = [{"name": service} for service in temp_list]
            output = {
                "result": result,
                "date": now
            }
        else:
            output = {
                "result": "No service found",
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get services name as {test}"
    else:
        log_msg = f"{remote_ip} tried to get services name as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/get_status_change_records_by_time", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def get_status_change_records_by_time():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    from_date = sanitizer(request.args.get("from_date"))
    if from_date is None:
        from_date = datetime.min
    else:
        from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")

    to_date = sanitizer(request.args.get("to_date"))
    if to_date is None:
        to_date = datetime.now()
    else:
        to_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")

    page = sanitizer(request.args.get("page", "1"))

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        statuses = Status.query.filter(and_
                                       (from_date <= func.DATETIME(Status.change_date),
                                        func.DATETIME(Status.change_date) < to_date)).paginate(
            page, per_page, error_out=False)
        total = statuses.total
        statuses = statuses.items
        result = statuses_schema.dump(statuses)
        if total > 0:
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No status change found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get UFW status change records as {test} from: {str(from_date)} to: {str(to_date)}"
    else:
        log_msg = f"{remote_ip} tried get UFW status change records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_status_change_records_by_user_id", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_status_change_records_by_user_id():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    userId = sanitizer(request.args.get("userId"))
    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5
    if userId is None or not userId.isnumeric():
        userId = 0
    else:
        userId = int(userId)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        statuses = None
        if userId != 0:
            statuses = Status.query.filter_by(user_id=userId).paginate(
                page, per_page, error_out=False)
            total = statuses.total
            statuses = statuses.items
            result = statuses_schema.dump(statuses)
            if total > 0:
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No status change found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            statuses = Status.query.paginate(
                page, per_page, error_out=False)
            total = statuses.total
            statuses = statuses.items
            result = statuses_schema.dump(statuses)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
            if total == 0:
                output = {
                    "result": "No status change found",
                    "total": 0,
                    "date": now
                }
                status_code = 404

        log_msg = f"{remote_ip} get UFW status change records as {test} for user_id: {str(userId)}"
    else:
        log_msg = f"{remote_ip} tried get UFW status change records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_all_rules", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_all_rules():
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
    if test and test.manager_privileges and not test.is_first:
        rules = Rule.query.paginate(
            page, per_page, error_out=False)
        total = rules.total
        rules = rules.items
        if total is not None and total > 0:
            result = rules_schema.dump(rules)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No rule found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get all rules UFW records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all rules UFW records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_rules_by_user_id", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_rules_by_user_id():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    userId = sanitizer(request.args.get("userId"))
    if userId is None or not userId.isnumeric():
        if userId != "-404":
            userId = 0
        else:
            userId = int(userId)
    else:
        userId = int(userId)

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        rules = None
        total = 0
        if userId != 0:
            rules = Rule.query.filter_by(user_id=userId).paginate(
                page, per_page, error_out=False)
            total = rules.total
            rules = rules.items
            if total is not None and total > 0:
                result = rules_schema.dump(rules)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No rule found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            output = {
                "result": "No route found",
                "total": 0,
                "date": now
            }
            status_code = 404
        log_msg = f"{remote_ip} get UFW rule records as {test} for user_id: {str(userId)}"
    else:
        log_msg = f"{remote_ip} tried get UFW rule records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_rules_by_type", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_rules_by_type():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    ruleAction = sanitizer(request.args.get("ruleAction", "all"))

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:

        rules = Rule.query.filter_by(
            rule_action=ruleAction).paginate(
            page, per_page, error_out=False)
        total = rules.total
        rules = rules.items
        if total is not None and total > 0:
            result = rules_schema.dump(rules)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No rule found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get rules with action type '{ruleAction}' as {test}"
    else:
        log_msg = f"{remote_ip} tried to get rules with action type '{ruleAction}' as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_all_deleted_rules", methods=["GET"])
@jwt_required(fresh=True)
def get_all_deleted_rules():
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
    if test and test.manager_privileges and not test.is_first:
        rules = DeletedRule.query.paginate(
            page, per_page, error_out=False)
        total = rules.total
        rules = rules.items
        if total is not None and total > 0:
            result = deleted_rules_schema.dump(rules)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No deleted rule found",
                "total": 0,
                "date": now
            }
            status_code = 404
        log_msg = f"{remote_ip} get all deleted rules UFW records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all deleted rules UFW records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/get_deleted_rules_by_user_id", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def get_deleted_rules_by_user_id():
    remote_ip = request.remote_addr
    output = []
    status_code = 200

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    deleter_userId = sanitizer(request.args.get("deleterUserId"))
    if deleter_userId is None or not deleter_userId.isnumeric():
        if deleter_userId != "-404":
            deleter_userId = 0
        else:
            deleter_userId = int(deleter_userId)
    else:
        deleter_userId = int(deleter_userId)
    adder_userId = sanitizer(request.args.get("adderUserId"))
    if adder_userId is None or not adder_userId.isnumeric():
        if adder_userId != "-404":
            adder_userId = 0
        else:
            adder_userId = int(adder_userId)
    else:
        adder_userId = int(adder_userId)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        rules = None
        if deleter_userId != 0 or adder_userId != 0:
            rules = DeletedRule.query.filter(
                or_(DeletedRule.deleter_user_id == deleter_userId,
                    DeletedRule.adder_user_id == adder_userId)).paginate(
                page, per_page, error_out=False)
            total = rules.total
            rules = rules.items
            if total is not None and total > 0:
                result = deleted_rules_schema.dump(rules)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No deleted rule with these ids found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            output = {
                "result": "No route found",
                "total": 0,
                "date": now
            }
            status_code = 404
        log_msg = f"{remote_ip} get UFW deleted rule records as {test} for deleter_user_id: {str(deleter_userId)} or adder_user_id: {str(adder_userId)}"
    else:
        log_msg = f"{remote_ip} tried get UFW deleted rule records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/get_deleted_rules_by_type", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def get_deleted_rules_by_type():
    remote_ip = request.remote_addr
    output = []
    status_code = 200
    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5
    ruleAction = sanitizer(request.args.get("ruleAction"))
    if ruleAction is None or ruleAction.lower() not in rule_actions:
        ruleAction = "all"
    else:
        ruleAction = ruleAction.lower()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        rules = None
        if ruleAction != "all":
            rules = DeletedRule.query.filter(
                DeletedRule.rule_command.like(f"{ruleAction}%")).paginate(
                page, per_page, error_out=False)
            total = rules.total
            rules = rules.items
            if total is not None and total > 0:
                result = deleted_rules_schema.dump(rules)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No rule with this type found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            rules = DeletedRule.query.paginate(
                page, per_page, error_out=False)
            total = rules.total
            rules = rules.items
            result = deleted_rules_schema.dump(rules)
            output = {
                "result": result,
                "total": total,
                "date": now
            }

        log_msg = f"{remote_ip} get deleted rules with action type '{ruleAction}' as {test}"
    else:
        log_msg = f"{remote_ip} tried to get deleted rules with action type '{ruleAction}' as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_all_routes", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_all_routes():
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
    if test and test.manager_privileges and not test.is_first:
        routes = Route.query.paginate(
            page, per_page, error_out=False)
        total = routes.total
        routes = routes.items
        if total is not None and total > 0:
            result = routes_schema.dump(routes)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No route found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get all routes UFW records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all route UFW records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_routes_by_user_id", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_routes_by_user_id():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    userId = sanitizer(request.args.get("userId"))
    if userId is None or not userId.isnumeric():
        if userId != "-404":
            userId = 0
        else:
            userId = int(userId)
    else:
        userId = int(userId)

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        routes = None
        total = 0
        if userId != 0:
            routes = Route.query.filter_by(user_id=userId).paginate(
                page, per_page, error_out=False)
            total = routes.total
            routes = routes.items
            if total is not None and total > 0:
                result = routes_schema.dump(routes)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No route found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            output = {
                "result": "No route found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get UFW route records as {test} for user_id: {str(userId)}"
    else:
        log_msg = f"{remote_ip} tried get UFW route records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_routes_by_type", methods=["GET"])
@jwt_required(fresh=True)
@cross_origin()
def get_routes_by_type():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    routeAction = sanitizer(request.args.get("routeAction", "all"))

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        routes = Route.query.filter_by(
            route_action=routeAction).paginate(
            page, per_page, error_out=False)
        total = routes.total
        routes = routes.items
        if total is not None and total > 0:
            result = routes_schema.dump(routes)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No route found",
                "total": 0,
                "date": now
            }
            status_code = 404

        log_msg = f"{remote_ip} get routes with action type '{routeAction}' as {test}"
    else:
        log_msg = f"{remote_ip} tried to get routes with action type '{routeAction}' as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "total": 0,
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/get_all_deleted_routes", methods=["GET"])
@jwt_required(fresh=True)
def get_all_deleted_routes():
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
    if test and test.manager_privileges and not test.is_first:
        routes = DeletedRoute.query.paginate(
            page, per_page, error_out=False)
        total = routes.total
        routes = routes.items
        if total is not None and total > 0:
            result = deleted_routes_schema.dump(routes)
            output = {
                "result": result,
                "total": total,
                "date": now
            }
        else:
            output = {
                "result": "No deleted route found",
                "total": 0,
                "date": now
            }
            status_code = 404
        log_msg = f"{remote_ip} get all deleted routes UFW records as {test}"
    else:
        log_msg = f"{remote_ip} tried to get all deleted routes UFW records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/get_deleted_routes_by_user_id", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def get_deleted_routes_by_user_id():
    remote_ip = request.remote_addr
    output = []
    status_code = 200

    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5

    deleter_userId = sanitizer(request.args.get("deleterUserId"))
    if deleter_userId is None or not deleter_userId.isnumeric():
        if deleter_userId != "-404":
            deleter_userId = 0
        else:
            deleter_userId = int(deleter_userId)
    else:
        deleter_userId = int(deleter_userId)
    adder_userId = sanitizer(request.args.get("adderUserId"))
    if adder_userId is None or not adder_userId.isnumeric():
        if adder_userId != "-404":
            adder_userId = 0
        else:
            adder_userId = int(adder_userId)
    else:
        adder_userId = int(adder_userId)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        routes = None
        if deleter_userId != 0 or adder_userId != 0:
            routes = DeletedRoute.query.filter(
                or_(DeletedRoute.deleter_user_id == deleter_userId,
                    DeletedRoute.adder_user_id == adder_userId)).paginate(
                page, per_page, error_out=False)
            total = routes.total
            routes = routes.items
            if total is not None and total > 0:
                result = deleted_routes_schema.dump(routes)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No deleted route with these ids found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            output = {
                "result": "No deleted route with these ids found",
                "total": 0,
                "date": now
            }
            status_code = 404
        log_msg = f"{remote_ip} get UFW deleted route records as {test} for deleter_user_id: {str(deleter_userId)} or adder_user_id: {str(adder_userId)}"
    else:
        log_msg = f"{remote_ip} tried get UFW deleted route records as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/get_deleted_routes_by_type", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def get_deleted_routes_by_type():
    remote_ip = request.remote_addr
    output = []
    status_code = 200
    page = sanitizer(request.args.get("page", "1"))
    page = int(page) if page is not None and page.isdigit() else 1
    per_page = sanitizer(request.args.get("perPage", "5"))
    per_page = int(
        per_page) if per_page is not None and per_page.isdigit() else 5
    routeAction = sanitizer(request.args.get("routeAction"))
    if routeAction is None or routeAction.lower() not in rule_actions:
        routeAction = "all"
    else:
        routeAction = routeAction.lower()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges and not test.is_first:
        routes = None
        if routeAction != "all":
            routes = DeletedRoute.query.filter(
                DeletedRoute.route_command.like(f"%{routeAction}%")).paginate(
                page, per_page, error_out=False)
            total = routes.total
            routes = routes.items
            if total is not None and total > 0:
                result = deleted_routes_schema.dump(routes)
                output = {
                    "result": result,
                    "total": total,
                    "date": now
                }
            else:
                output = {
                    "result": "No route with this type found",
                    "total": 0,
                    "date": now
                }
                status_code = 404
        else:
            routes = DeletedRoute.query.paginate(
                page, per_page, error_out=False)
            total = routes.total
            routes = routes.items
            result = deleted_routes_schema.dump(routes)
            output = {
                "result": result,
                "total": total,
                "date": now
            }

        log_msg = f"{remote_ip} get deleted routes with action type '{routeAction}' as {test}"
    else:
        log_msg = f"{remote_ip} tried to get deleted routes with action type '{routeAction}' as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/status", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def status():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        cmd = ["ufw", "status"]
        status = run_cmd(cmd)
        status = (status.replace("-", " ").splitlines())
        status = [
            " ".join(item.split()) for item in status if len(item) != 0]
        status = [
            item for item in status if len(item) != 0 and "To Action From" not in item]

        output = {
            "result": status,
            "date": now
        }

        log_msg = f"{remote_ip} check UFW status as {test}"
    else:
        log_msg = f"{remote_ip} tried check UFW status as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": ["Unauthorized user"],
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/enable", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def enable():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        status = check_ufw_status()
        if "Status: active\n" not in status:
            cmd = ["ufw", "enable"]
            result = run_cmd(cmd)
            output = {
                "result": result,
                "date":  now
            }
            if "enabled" in result:
                status_record = Status(
                    user_id=test.id, ufw_status=True)
                db.session.add(status_record)
                db.session.commit()
        else:
            output = {
                "result": "Firewall is already enabled",
                "date":  now
            }
            result = output.get("result", "")
        log_msg = f"{remote_ip} as {test} tried to enable UFW with result {result}"

    else:
        log_msg = f"{remote_ip} as {test} tried to enable UFW and failed because of Unauthorized user"
        log_tag = "ALERT"
        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/disable", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def disable():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        status = check_ufw_status()
        if "Status: inactive\n" not in status:
            cmd = ["ufw", "disable"]
            result = run_cmd(cmd)
            output = {
                "result": result,
                "date":  now
            }
            if "disable" in result:
                status_record = Status(
                    user_id=test.id, ufw_status=False)
                db.session.add(status_record)
                db.session.commit()
        else:
            output = {
                "result": "Firewall is already disabled",
                "date":  now
            }
        result = output["result"]
        log_msg = f"{remote_ip} as {test} tried to disable UFW with result {result}"

    else:
        log_msg = f"{remote_ip} as {test} tried to disable UFW and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date":  now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/reload", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def reload():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now_datetime_obj = datetime.now()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        cmd = ["ufw", "reload"]
        result = run_cmd(cmd)

        output = {
            "result": result,
            "date": now
        }

        log_msg = f"{remote_ip} as {test} tried to reload UFW with result {result}"
    else:
        log_msg = f"{remote_ip} as {test} tried to reload UFW and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ufw_manager_blueprint.route("/reset", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def reset():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        cmd = ["ufw", "--force", "reset"]
        result = run_cmd(cmd)
        if "Backing up" in result:
            rules = Rule.query.all()
            for rule in rules:
                deleted_rule = DeletedRule(
                    adder_user_id=rule.user_id, deleter_user_id=test.id, rule_command=rule.rule_command,
                    add_date=rule.add_date)
                db.session.delete(rule)
                db.session.add(deleted_rule)
            routes = Route.query.all()
            for route in routes:
                deleted_route = DeletedRoute(
                    adder_user_id=route.user_id, deleter_user_id=test.id, route_command=route.route_command,
                    add_date=route.add_date)
                db.session.delete(route)
                db.session.add(deleted_route)
            db.session.commit()
            result = "all rules/routes deleted and ufw disabled"
        output = {
            "result": result,
            "date": now
        }

        log_msg = f"{remote_ip} as {test} tried to reset UFW with result {result}"
    else:
        log_msg = f"{remote_ip} as {test} tried to reset UFW and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/update_rules", methods=["GET"])
@ jwt_required(fresh=True)
@ cross_origin()
def update_rules():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        cmd = ['ufw', 'show', 'added']
        output = run_cmd(cmd)
        output = output.splitlines()[1:]
        output = [rule.replace("'", "").replace("ufw ", "") for rule in output]
        routes = Route.query.all()
        rules = Rule.query.all()
        rules_update_counter = 0

        for route in routes:
            if route.route_command not in output:
                deleted_route = DeletedRoute(
                    adder_user_id=route.user_id,
                    deleter_user_id=-404,
                    route_command=route.route_command,
                    add_date=route.add_date)
                db.session.delete(route)
                db.session.add(deleted_route)
                rules_update_counter += 1
            else:
                output.remove(route.route_command)
        for rule in rules:
            if rule.rule_command not in output:
                deleted_rule = DeletedRule(
                    adder_user_id=rule.user_id,
                    deleter_user_id=-404,
                    rule_command=rule.rule_command,
                    add_date=rule.add_date)
                db.session.delete(rule)
                db.session.add(deleted_rule)
                rules_update_counter += 1
            else:
                output.remove(rule.rule_command)

        for rule in output:
            if rule.__contains__('(None)'):
                break
            action = ''
            comment = None
            for act in rule_actions:
                if act in rule:
                    action = act
                    break
            if 'comment' in rule:
                comment = rule.split('comment ')[1]
            if 'route' in rule:
                route = Route(
                    user_id=-404,
                    route_command=rule,
                    route_action=action)
                if comment is not None:
                    route.comment = comment
                db.session.add(route)
                rules_update_counter += 1
            else:
                in_out = 'in'
                if 'out' in rule:
                    in_out = 'out'

                rule = Rule(
                    user_id=-404,
                    rule_command=rule,
                    rule_action=action,
                    in_out=in_out)
                if comment is not None:
                    rule.comment = comment
                db.session.add(rule)
                rules_update_counter += 1
        db.session.commit()
        result = f"{rules_update_counter} rules/routes updated and all tables are up to date."
        output = {
            "result": result,
            "date": now
        }

        log_msg = f"{remote_ip} as {test} tried to update rules/routes table UFW with result {result}"
    else:
        log_msg = f"{remote_ip} as {test} tried to update rules/routes table UFW and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/add_rule", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def add_rule():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    log_msg = ""
    log_tag = "INFO"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        json_data = request.get_json()
        rule_action = sanitizer(json_data.get("rule_action"))
        if rule_action is not None:
            enable_cmd = ["ufw", "enable"]
            enable_result = run_cmd(enable_cmd)
            args_dict, cmd, is_args_list_set = set_args_for_rule(
                args=json_data, rule_action=rule_action)
            if is_args_list_set:

                from_service_name = None
                to_service_name = None
                if args_dict.get("from_service_name") is not None:
                    from_service_name = args_dict.pop("from_service_name")
                if args_dict.get("to_service_name") is not None:
                    to_service_name = args_dict.pop("to_service_name")

                result = run_cmd(cmd)
                cmd.remove("ufw")
                rule_command = " ".join(cmd)
                if "Rule added" in result:
                    rule = Rule(
                        user_id=test.id, rule_command=rule_command,
                        rule_action=rule_action, in_out=args_dict.get("in_out"))

                    if args_dict.get("from_IP") is not None:
                        rule.from_IP = args_dict.get("from_IP")
                    if args_dict.get("from_port") is not None:
                        rule.from_port = args_dict.get("from_port")
                    if from_service_name is not None:
                        rule.from_service_name = from_service_name
                    if args_dict.get("to_IP") is not None:
                        rule.to_IP = args_dict.get("to_IP")
                    if args_dict.get("to_port") is not None:
                        rule.to_port = args_dict.get("to_port")
                    if to_service_name is not None:
                        rule.to_service_name = to_service_name

                    if args_dict.get("protocol") is not None:
                        rule.protocol = args_dict.get("protocol")
                    else:
                        rule.protocol = "tcp/udp"

                    if args_dict.get("comment") is not None:
                        rule.comment = args_dict.get("comment")

                    db.session.add(rule)
                    db.session.commit()
                    log_msg = f"{remote_ip} as {test} add this rule: '{rule_command}' "
                elif "Rule updated" in result or "WARN: Rule changed after normalization" in result:
                    query_filter = rule_command.split(" comment")[0]
                    rule = Rule.query.filter(
                        Rule.rule_command.like(f"{query_filter}%")).first()
                    rule.rule_command = rule_command
                    if args_dict.get("comment") is not None:
                        rule.comment = args_dict.get("comment")
                    else:
                        rule.comment = None
                    db.session.add(rule)
                    db.session.commit()
                    log_msg = f"{remote_ip} as {test} update this rule: '{rule_command}' "
                else:
                    if "Skipping adding existing rule" in result:
                        log_msg = f"{remote_ip} as {test} tried to add this rule: '{rule_command}' but rule exist"
                    else:
                        log_msg = f"{remote_ip} as {test} tried to add this rule: '{rule_command}' but failed because of {result}"
            else:
                result = "Bad request."
                status_code = 400
                log_msg = f"{remote_ip} as {test} tried to add rule to UFW and failed because bad request"
        else:
            result = "Bad request."
            status_code = 400
            log_msg = f"{remote_ip} as {test} tried to add rule to UFW and failed because bad request"
    else:
        result = "Unauthorized user"
        log_msg = f"{remote_ip} as {test} tried to add rule to UFW and failed because of Unauthorized user"
        log_tag = "ALERT"
        status_code = 403

    if result == "" or result is None:
        result = "Bad requst something like -> Mixed IP versions for 'from' and 'to'"
        status_code = 400

    output = {
        "result": result,
        "date": now
    }

    add_log(log_msg, log_tag=log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/delete_rule", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def delete_rule():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        json_data = request.get_json()
        args_dict, cmd, is_args_list_set = set_args_for_rule(
            args=json_data, rule_action="delete")
        if is_args_list_set:
            result = run_cmd(cmd)
            cmd.remove("ufw")
            cmd.remove("delete")
            rule_command = " ".join(cmd)
            rule = Rule.query.filter_by(rule_command=rule_command).first()
            if rule:
                db.session.delete(rule)
                db.session.commit()
                log_msg = f"{remote_ip} as {test} delete this rule: '{rule_command}'"
                deleted_rule = DeletedRule(
                    adder_user_id=rule.user_id, deleter_user_id=test.id, rule_command=rule_command,
                    add_date=rule.add_date)
                db.session.add(deleted_rule)
                db.session.commit()
                add_log(
                    f"{remote_ip} as {test} add deleted rule to delete_rule table")
            else:
                log_msg = f"{remote_ip} as {test} tried to delete this rule: '{rule_command}' and failed because rule not exist"
        else:
            result = "Bad request."
            status_code = 400
            log_msg = f"{remote_ip} as {test} tried to delete rule from UFW and failed because bad request"

    else:
        result = "Unauthorized user"
        log_msg = f"{remote_ip} as {test} tried to delete rule from UFW and failed because of Unauthorized user"
        log_tag = "ALERT"
        status_code = 403

    if result == "" or result is None:
        result = "Bad requst something like -> Mixed IP versions for 'from' and 'to'"
        status_code = 400

    output = {
        "result": result,
        "date": now
    }

    add_log(log_msg, log_tag=log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/delete_rule_by_id", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def delete_rule_by_id():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    json_data = request.get_json()
    rule_id = sanitizer(json_data.get("ruleId", 0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        rule = None
        if rule_id is not None and rule_id != "0":
            rule = Rule.query.filter_by(id=rule_id)
            if rule.first() is not None:
                rule = rule.first()
                cmd = "ufw delete " + rule.rule_command
                cmd = cmd.split(" ")
                result = run_cmd(cmd)
                deleted_rule = DeletedRule(
                    adder_user_id=rule.user_id, deleter_user_id=test.id, rule_command=rule.rule_command,
                    add_date=rule.add_date)
                db.session.delete(rule)
                db.session.add(deleted_rule)
                db.session.commit()

                log_msg = f"{remote_ip} as {test} delete this rule: '{rule.rule_command}'"
                add_log(
                    f"{remote_ip} as {test} add deleted rule to delete_rule table")
            else:
                result = f"there is no rule with rule id: {rule_id}"
                status_code = 404
            output = {
                "result": result,
                "date": now
            }

        else:
            result = "Bad Request you need to send rule ID as ruleId in json."
            output = {
                "result": result,
                "date": now
            }
            status_code = 400

        log_msg = f"{remote_ip} as {test} delete this rule {rule_id} as {test}"
    else:
        log_msg = f"{remote_ip} tried to delete this rule {rule_id} as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/add_route", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def add_route():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    log_msg = ""
    log_tag = "INFO"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        json_data = request.get_json()
        route_action = sanitizer(json_data.get("route_action"))
        if route_action is not None:
            enable_cmd = ["ufw", "enable"]
            enable_result = run_cmd(enable_cmd)
            args_dict, cmd, is_args_list_set = set_args_for_route(
                args=json_data, route_action=route_action)
            if is_args_list_set:

                from_service_name = None
                to_service_name = None
                if args_dict.get("from_service_name") is not None:
                    from_service_name = args_dict.pop("from_service_name")
                if args_dict.get("to_service_name") is not None:
                    to_service_name = args_dict.pop("to_service_name")
                result = run_cmd(cmd)
                cmd.remove("ufw")
                route_command = " ".join(cmd)
                if "Rule added" in result:
                    route = Route(
                        user_id=test.id, route_command=route_command,
                        route_action=route_action)

                    if args_dict.get("_in") is not None:
                        route._in = args_dict.get("_in")
                    if args_dict.get("in_on") is not None:
                        route.in_on = args_dict.get("in_on")
                    if args_dict.get("_out") is not None:
                        route._out = args_dict.get("_out")
                    if args_dict.get("out_on") is not None:
                        route.out_on = args_dict.get("out_on")
                    if args_dict.get("from_IP") is not None:
                        route.from_IP = args_dict.get("from_IP")
                    if args_dict.get("from_port") is not None:
                        route.from_port = args_dict.get("from_port")
                    if from_service_name is not None:
                        route.from_service_name = from_service_name
                    if args_dict.get("to_IP") is not None:
                        route.to_IP = args_dict.get("to_IP")
                    if args_dict.get("to_port") is not None:
                        route.to_port = args_dict.get("to_port")
                    if to_service_name is not None:
                        route.to_service_name = to_service_name

                    if args_dict.get("protocol") is not None:
                        route.protocol = args_dict.get("protocol")
                    else:
                        route.protocol = "tcp/udp"

                    if args_dict.get("comment") is not None:
                        route.comment = args_dict.get("comment")

                    db.session.add(route)
                    db.session.commit()
                    log_msg = f"{remote_ip} as {test} add this route: '{route_command}' "
                elif "Rule updated" in result or "WARN: Rule changed after normalization" in result:
                    query_filter = route_command.split(" comment")[0]
                    route = Route.query.filter(
                        Route.route_command.like(f"{query_filter}%")).first()
                    print(route)
                    route.route_command = route_command
                    if args_dict.get("comment") is not None:
                        route.comment = args_dict.get("comment")
                    else:
                        route.comment = None
                    db.session.add(route)
                    db.session.commit()
                    log_msg = f"{remote_ip} as {test} update this route: '{route_command}' "
                else:
                    if "Skipping adding existing Rule" in result:
                        log_msg = f"{remote_ip} as {test} tried to add this route: '{route_command}' but rule exist"
                    else:
                        log_msg = f"{remote_ip} as {test} tried to add this route: '{route_command}' but failed because of {result}"
            else:
                result = "Bad request."
                status_code = 400
                log_msg = f"{remote_ip} as {test} tried to add route to UFW and failed because bad request"
        else:
            result = "Bad request."
            status_code = 400
            log_msg = f"{remote_ip} as {test} tried to add route to UFW and failed because bad request"
    else:
        result = "Unauthorized user"
        log_msg = f"{remote_ip} as {test} tried to add route to UFW and failed because of Unauthorized user"
        log_tag = "ALERT"
        status_code = 403

    if result == "" or result is None:
        result = "Bad requst something like -> Mixed IP versions for 'from' and 'to'"
        status_code = 400

    output = {
        "result": result,
        "date": now
    }

    add_log(log_msg, log_tag=log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/delete_route", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def delete_route():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        json_data = request.get_json()
        args_dict, cmd, is_args_list_set = set_args_for_route(
            args=json_data, route_action="delete")
        if is_args_list_set:
            result = run_cmd(cmd)
            cmd.remove("ufw")
            cmd.remove("delete")
            route_command = " ".join(cmd)
            route = Route.query.filter_by(route_command=route_command).first()
            if route:
                db.session.delete(route)
                db.session.commit()
                log_msg = f"{remote_ip} as {test} delete this route: '{route_command}'"
                deleted_route = DeletedRoute(
                    adder_user_id=route.user_id, deleter_user_id=test.id, route_command=route_command,
                    add_date=route.add_date)
                db.session.add(deleted_route)
                db.session.commit()
                add_log(
                    f"{remote_ip} as {test} add deleted route to delete_route table")
            else:
                log_msg = f"{remote_ip} as {test} tried to delete this route: '{route_command}' and failed because route not exist"
        else:
            result = "Bad request."
            status_code = 400
            log_msg = f"{remote_ip} as {test} tried to delete route from UFW and failed because bad request"

    else:
        result = "Unauthorized user"
        log_msg = f"{remote_ip} as {test} tried to delete route from UFW and failed because of Unauthorized user"
        log_tag = "ALERT"
        status_code = 403

    if result == "" or result is None:
        result = "Bad requst something like -> Mixed IP versions for 'from' and 'to'"
        status_code = 400

    output = {
        "result": result,
        "date": now
    }

    add_log(log_msg, log_tag=log_tag)

    return jsonify(output), status_code


@ ufw_manager_blueprint.route("/delete_route_by_id", methods=["POST"])
@ jwt_required(fresh=True)
@ cross_origin()
def delete_route_by_id():
    remote_ip = request.remote_addr
    output = {}
    status_code = 200
    json_data = request.get_json()
    route_id = sanitizer(json_data.get("routeId", 0))
    print(type(route_id))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.manager_privileges and not test.is_first:
        route = None
        if route_id is not None and route_id != "0":
            route = Route.query.filter_by(id=route_id)
            if route.first() is not None:
                route = route.first()
                route_command = route.route_command.split(" ")
                route_command.insert(1, "delete")
                route_command.insert(0, "ufw")
                cmd = route_command
                result = run_cmd(cmd)
                deleted_route = DeletedRoute(
                    adder_user_id=route.user_id, deleter_user_id=test.id, route_command=route.route_command,
                    add_date=route.add_date)
                db.session.delete(route)
                db.session.add(deleted_route)
                db.session.commit()

                log_msg = f"{remote_ip} as {test} delete this route: '{route.route_command}'"
                add_log(
                    f"{remote_ip} as {test} add deleted route to delete_route table")
            else:
                result = f"there is no route with route id: {route_id}"
                status_code = 404
            output = {
                "result": result,
                "date": now
            }

        else:
            result = "Bad Request you need to send route ID as routeId in json."
            output = {
                "result": result,
                "date": now
            }
            status_code = 400

        log_msg = f"{remote_ip} as {test} delete this route {route_id} as {test}"
    else:
        log_msg = f"{remote_ip} tried to delete this route {route_id} as {test} and failed because of Unauthorized user"
        log_tag = "ALERT"

        output = {
            "result": "Unauthorized user",
            "date": now
        }
        status_code = 403

    add_log(log_msg, log_tag)

    return jsonify(output), status_code


def set_args_for_rule(args, rule_action):
    args_dict = {"ufw": "ufw", "rule_action": rule_action}
    is_args_list_set = False

    if rule_action == "delete":
        rule_type_delete = sanitizer(args.get("rule_type_delete"))
        if rule_type_delete is not None:
            args_dict["rule_type_delete"] = rule_type_delete
        else:
            return None, None, is_args_list_set

    protocol = None
    in_out = sanitizer(args.get("in_out"))
    if in_out is not None and "out" in in_out:
        args_dict["in_out"] = "out"
    else:
        args_dict["in_out"] = "in"

    args_dict["from"] = "from"
    from_IP = sanitizer(args.get("from_IP"))
    if from_IP is not None and validIPAddress(from_IP) != "invalid":
        args_dict["from_IP"] = from_IP
    else:
        args_dict["from_IP"] = "any"

    from_service_name = sanitizer(args.get("from_service_name"))
    if from_service_name is not None:
        services = Service.query.filter_by(
            service_name=from_service_name).all()
        port = ""
        if len(services) == 1:
            portAndProto = services[0].service_port.split("/")
            port = portAndProto[0]
            protocol = portAndProto[1]
        elif len(services) > 1:
            port = services[0].service_port.split("/")[0]
        args_dict["from_service_name"] = from_service_name
        args_dict["f_port"] = "port"
        args_dict["from_port"] = f"{port}"
    else:
        port = sanitizer(args.get("from_port"))
        if port is not None:
            args_dict["f_port"] = "port"
            args_dict["from_port"] = f"{port}"

    args_dict["to"] = "to"
    to_IP = sanitizer(args.get("to_IP"))
    if to_IP is not None and validIPAddress(to_IP) != "invalid":
        args_dict["to_IP"] = to_IP
    else:
        args_dict["to_IP"] = "any"

    to_service_name = sanitizer(args.get("to_service_name"))
    if to_service_name is not None:
        services = Service.query.filter_by(service_name=to_service_name).all()
        if len(services) == 1:
            portAndProto = services[0].service_port.split("/")
            port = portAndProto[0]
            protocol = portAndProto[1]
        elif len(services) > 1:
            port = services[0].service_port.split("/")[0]
        args_dict["to_service_name"] = to_service_name
        args_dict["t_port"] = "port"
        args_dict["to_port"] = f"{port}"
    else:
        port = sanitizer(args.get("to_port"))
        if port is not None:
            args_dict["t_port"] = "port"
            args_dict["to_port"] = f"{port}"

    _protocol = sanitizer(args.get("protocol"))
    if _protocol is not None and _protocol in rule_protocols:
        index = rule_protocols.index(_protocol)
        if 0 < index <= 2:
            args_dict["proto"] = "proto"
            args_dict["protocol"] = _protocol
        elif index > 2:
            if _protocol == "ah" or _protocol == "esp" or _protocol == "gre":
                if args_dict.get("from_port"):
                    args_dict.pop("f_port")
                    args_dict.pop("from_port")
                if args_dict.get("to_port"):
                    args_dict.pop("t_port")
                    args_dict.pop("to_port")
                args_dict["proto"] = "proto"
                args_dict["protocol"] = _protocol
            elif _protocol == "ipv6" or _protocol == "igmp":
                is_from_IPv4 = (
                    validIPAddress(from_IP) == "IPv4" or validIPAddress(from_IP) == "invalid")
                is_to_IPv4 = (
                    validIPAddress(to_IP) == "IPv4" or validIPAddress(to_IP) == "invalid")
                if not is_from_IPv4 or not is_to_IPv4:
                    args_dict["proto"] = "proto"
                    args_dict["protocol"] = _protocol
                    if not is_from_IPv4:
                        args_dict["from_IP"] = "any"
                    if args_dict.get("from_port"):
                        args_dict.pop("f_port")
                        args_dict.pop("from_port")
                    if not is_to_IPv4:
                        args_dict["to_IP"] = "any"
                    if args_dict.get("to_port"):
                        args_dict.pop("t_port")
                        args_dict.pop("to_port")
    elif protocol is not None:
        args_dict["proto"] = "proto"
        args_dict["protocol"] = protocol

    comment = sanitizer(args.get("comment"))
    if comment is not None and comment != "" and len(comment) <= 255:
        args_dict["has_comment"] = "comment"
        args_dict["comment"] = f'{comment}'
    elif comment is not None and len(comment) > 255:
        args_dict["has_comment"] = "comment"
        args_dict["comment"] = 'your comment is too long'

    if args_dict.get("from_service_name") is None and args_dict.get("protocol") is not None and args_dict.get("from_port") is not None:
        from_service_name = Service.query.filter_by(
            service_port=f'{args_dict["from_port"]}/{args_dict["protocol"]}').first()
        if from_service_name is not None:
            args_dict["from_service_name"] = from_service_name.service_name

    if args_dict.get("to_service_name") is None and args_dict.get("protocol") is not None and args_dict.get("to_port") is not None:
        to_service_name = Service.query.filter_by(
            service_port=f'{args_dict["to_port"]}/{args_dict["protocol"]}').first()
        if to_service_name is not None:
            args_dict["to_service_name"] = to_service_name.service_name
    is_args_list_set = True
    args_list = [args_dict[key] for key in args_dict if key !=
                 "from_service_name" and key != "to_service_name"]
    return args_dict, args_list, is_args_list_set


def set_args_for_route(args, route_action):
    args_dict = {"ufw": "ufw", "route": "route", "route_action": route_action}
    is_args_list_set = False

    if route_action == "delete":
        route_type_delete = sanitizer(args.get("route_type_delete"))
        if route_type_delete is not None:
            args_dict["route_type_delete"] = route_type_delete
        else:
            return None, None, is_args_list_set

    protocol = None
    _in = sanitizer(args.get("_in"))
    if _in is not None:
        in_on = sanitizer(args.get("in_on"))
        args_dict["_in"] = "in"
        if in_on is not None:
            args_dict["on_in"] = "on"
            args_dict["in_on"] = in_on

    _out = sanitizer(args.get("_out"))
    out_on = sanitizer(args.get(""))
    if _out is not None:
        out_on = sanitizer(args.get("out_on"))
        args_dict["_out"] = "out"
        if out_on is not None:
            args_dict["on_out"] = "on"
            args_dict["out_on"] = out_on

    args_dict["from"] = "from"
    from_IP = sanitizer(args.get("from_IP"))
    if from_IP is not None and validIPAddress(from_IP) != "invalid":
        args_dict["from_IP"] = from_IP
    else:
        args_dict["from_IP"] = "any"

    from_service_name = sanitizer(args.get("from_service_name"))
    if from_service_name is not None:
        services = Service.query.filter_by(
            service_name=from_service_name).all()
        port = ""
        if len(services) == 1:
            portAndProto = services[0].service_port.split("/")
            port = portAndProto[0]
            protocol = portAndProto[1]
        elif len(services) > 1:
            port = services[0].service_port.split("/")[0]
        args_dict["from_service_name"] = from_service_name
        args_dict["f_port"] = "port"
        args_dict["from_port"] = f"{port}"
    else:
        port = sanitizer(args.get("from_port"))
        if port is not None:
            args_dict["f_port"] = "port"
            args_dict["from_port"] = f"{port}"

    args_dict["to"] = "to"
    to_IP = sanitizer(args.get("to_IP"))
    if to_IP is not None and validIPAddress(to_IP) != "invalid":
        args_dict["to_IP"] = to_IP
    else:
        args_dict["to_IP"] = "any"

    to_service_name = sanitizer(args.get("to_service_name"))
    if to_service_name is not None:
        services = Service.query.filter_by(service_name=to_service_name).all()
        if len(services) == 1:
            portAndProto = services[0].service_port.split("/")
            port = portAndProto[0]
            protocol = portAndProto[1]
        elif len(services) > 1:
            port = services[0].service_port.split("/")[0]
        args_dict["to_service_name"] = to_service_name
        args_dict["t_port"] = "port"
        args_dict["to_port"] = f"{port}"
    else:
        port = sanitizer(args.get("to_port"))
        if port is not None:
            args_dict["t_port"] = "port"
            args_dict["to_port"] = f"{port}"

    _protocol = sanitizer(args.get("protocol"))
    if _protocol is not None and _protocol in rule_protocols:
        index = rule_protocols.index(_protocol)
        if 0 < index <= 2:
            args_dict["proto"] = "proto"
            args_dict["protocol"] = _protocol
        elif index > 2:
            if _protocol == "ah" or _protocol == "esp" or _protocol == "gre":
                if args_dict.get("from_port"):
                    args_dict.pop("f_port")
                    args_dict.pop("from_port")
                if args_dict.get("to_port"):
                    args_dict.pop("t_port")
                    args_dict.pop("to_port")
                args_dict["proto"] = "proto"
                args_dict["protocol"] = _protocol
            elif _protocol == "ipv6" or _protocol == "igmp":
                is_from_IPv4 = (
                    validIPAddress(from_IP) == "IPv4" or validIPAddress(from_IP) == "invalid")
                is_to_IPv4 = (
                    validIPAddress(to_IP) == "IPv4" or validIPAddress(to_IP) == "invalid")
                if not is_from_IPv4 or not is_to_IPv4:
                    args_dict["proto"] = "proto"
                    args_dict["protocol"] = _protocol
                    if not is_from_IPv4:
                        args_dict["from_IP"] = "any"
                    if args_dict.get("from_port"):
                        args_dict.pop("f_port")
                        args_dict.pop("from_port")
                    if not is_to_IPv4:
                        args_dict["to_IP"] = "any"
                    if args_dict.get("to_port"):
                        args_dict.pop("t_port")
                        args_dict.pop("to_port")
    elif protocol is not None:
        args_dict["proto"] = "proto"
        args_dict["protocol"] = protocol

    comment = sanitizer(args.get("comment"))
    if comment is not None and comment != "" and len(comment) <= 255:
        args_dict["has_comment"] = "comment"
        args_dict["comment"] = f'{comment}'
    elif comment is not None and len(comment) > 255:
        args_dict["has_comment"] = "comment"
        args_dict["comment"] = 'your comment is too long'

    if args_dict.get("from_service_name") is None and args_dict.get("protocol") is not None and args_dict.get("from_port") is not None:
        from_service_name = Service.query.filter_by(
            service_port=f'{args_dict["from_port"]}/{args_dict["protocol"]}').first()
        if from_service_name is not None:
            args_dict["from_service_name"] = from_service_name.service_name

    if args_dict.get("to_service_name") is None and args_dict.get("protocol") is not None and args_dict.get("to_port") is not None:
        to_service_name = Service.query.filter_by(
            service_port=f'{args_dict["to_port"]}/{args_dict["protocol"]}').first()
        if to_service_name is not None:
            args_dict["to_service_name"] = to_service_name.service_name
    is_args_list_set = True
    args_list = [args_dict[key] for key in args_dict if key !=
                 "from_service_name" and key != "to_service_name"]
    return args_dict, args_list, is_args_list_set


def validIPAddress(IP: str) -> str:
    try:
        if "/" in IP:
            IP = IP.split("/")[0]
        return "IPv4" if (type(ip_address(IP)) is IPv4Address) else "IPv6"
    except ValueError:
        return "invalid"


def bool_checker(param):
    return param is not None and param.isdigit() and bool(int(param))


def check_ufw_status():
    cmd = ["ufw", "status"]
    result = run_cmd(cmd)
    return result


def update_service_table():
    cmd = ['less', '/etc/services']

    result = subprocess.run(
        cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE).stdout.decode()
    result = result.splitlines()
    serviceList = []
    for item in result:
        if item.startswith("#") or len(item) == 0:
            continue
        item = item.split()
        if len(item) < 3:
            item.append("")
        else:
            item[2] = " ".join(item[2:])
        item = item[:3]
        serviceList.append({
            "service_name": item[0],
            "service_port": item[1],
            "service_comment": item[2]
        })
    services = Service.query.all()
    if len(services) < len(serviceList):
        Service.query.delete()
        service = [Service(
            service_name=item["service_name"],
            service_port=item["service_port"],
            service_comment=item["service_comment"]) for item in serviceList]
        db.session.add_all(service)
        db.session.commit()


def run_cmd(cmd):
    try:
        return subprocess.run(cmd, shell=False, stdout=subprocess.PIPE).stdout.decode()
    except Exception as e:
        error_message = repr(e)
        add_log(log=error_message, log_tag="ERROR")
        return error_message
