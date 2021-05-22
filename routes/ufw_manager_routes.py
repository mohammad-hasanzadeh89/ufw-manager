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
    if test and test.manager_privileges:
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
    from_date = request.args.get("from_date")
    if from_date is None:
        from_date = datetime.min
    else:
        from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")

    to_date = request.args.get("to_date")
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
    if test and test.admin_privileges:
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
    userId = request.args.get("userId")
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
    if test and test.admin_privileges:
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
    if test and test.manager_privileges:
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
    userId = int(userId) if userId is not None and userId.isnumeric() else 0

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
    if test and test.admin_privileges:
        rules = None
        total = 0
        if userId != 0:
            rules = Rule.query.filter_by(user_id=userId).paginate(
                page, per_page, error_out=False)
            total = rules.total
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
    if test and test.admin_privileges:

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
    if test and test.manager_privileges:
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

    deleter_userId = request.args.get("deleterUserId")
    if deleter_userId is None or not deleter_userId.isnumeric():
        deleter_userId = 0
    else:
        deleter_userId = int(deleter_userId)
    adder_userId = request.args.get("adderUserId")
    if adder_userId is None or not adder_userId.isnumeric():
        adder_userId = 0
    else:
        adder_userId = int(adder_userId)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = ""
    log_tag = "INFO"
    username = get_jwt_identity()
    test = User.query.filter_by(username=username).first()
    if test and test.admin_privileges:
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
    if test and test.admin_privileges:
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
    if test and test.manager_privileges:
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
    if test and test.manager_privileges:
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
    if test and test.manager_privileges:
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
    if test and test.manager_privileges:
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

# TODO delete all rule and delete them
# from rule table and add them to deleted rule
# @ufw_manager_blueprint.route("/reset", methods=["GET"])
# def reset():

# TODO update rules table if rule add manually


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
    if test and test.manager_privileges:
        json_data = request.get_json()
        rule_action = sanitizer(json_data.get("rule_action"))
        if rule_action is not None:
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
    if test and test.manager_privileges:
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
    if test and test.manager_privileges:
        rule = None
        if rule_id is not None:
            rule = Rule.query.filter_by(id=rule_id)
            if rule.first:
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


def set_args_for_rule(args, rule_action):
    args_dict = {"ufw": "ufw", "rule_action": rule_action}
    is_args_list_set = False

    if rule_action == "delete":
        rule_type_delete = sanitizer(args.get("rule_type_delete"))
        if rule_type_delete is not None:
            args_dict["rule_type_delete"] = rule_type_delete
        else:
            return None, is_args_list_set

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
