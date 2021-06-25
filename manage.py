import json
import os
import re
import getpass
import sqlite3
import bcrypt

from utilities.sanitizer import sanitizer
from utilities.logger import add_log
from utilities.select_menu import Menu


def create_admin():
    """
        The function create new admin user and add it to users table.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    resource_dir = os.path.join(base_dir, "resource")
    db_uri = os.path.join(resource_dir, "data_base.db")

    if os.path.exists(db_uri):
        connection = sqlite3.connect(db_uri)
        cursor = connection.cursor()
        user_table = cursor.execute(
            "SELECT * FROM sqlite_master"
        ).fetchall()
        if len(user_table) > 0:
            username = None
            password = None
            confirm_password = None
            while username is None:
                user_input = input(
                    "Please Enter a username with at least 4 character:\n")
                if len(user_input) >= 4:
                    user_input = sanitizer(user_input).lower()
                    if user_input:
                        test = cursor.execute(
                            f"SELECT * FROM users WHERE username = '{user_input}'").fetchone()
                        if test:
                            add_log("The username is not available.\n")
                        else:
                            username = user_input
                    else:
                        add_log(
                            "**username must have at least 4 character.\n")
                else:
                    add_log(
                        "**username must have at least 4 character.\n")
            while password is None:
                user_input = getpass.getpass(
                    "Please Enter a password with at least 8 character \n" +
                    "and password must contian lower-case, upper-case, \n" +
                    "digits and symbols like Test123!:\n")
                if check_pass_is_strong(user_input):
                    password = user_input
                else:
                    add_log("**weak password.\n")
            while confirm_password is None:
                user_input = getpass.getpass(
                    "Please confirm password:\n")
                if password == user_input:
                    confirm_password = user_input
                else:
                    add_log("**confirm password and password is not equal.\n")

            password = bcrypt.hashpw(
                bytes(password, 'utf-8'),
                bcrypt.gensalt(12)).decode()
            all_user = cursor.execute(
                "SELECT id FROM users").fetchall()
            cursor.execute(
                f"INSERT INTO users VALUES ({len(all_user) + 1}, '{username}', '{password}', 1, 1, 0, 0)")
            connection.commit()
            connection.close()
        else:
            add_log("users table does not exist.\nplease run the ufw-manager first.")
    else:
        add_log("please run the ufw-manager first.")


def rate_limit():
    """
        The function configure rate limiting.
    """
    limit_strings = []
    rate_limiting_string = ""
    periods = ['second', 'minute', 'hour', 'day']
    while len(limit_strings) < 4:
        limit_string = ""
        rate = None
        period = None
        user_select = Menu(
            periods,
            "Please select a period of time:")
        period = user_select()
        while rate is None:
            user_input = input(
                f"Please enter number requeset per {period}: (for example: 10)\n")
            if user_input.isdecimal():
                rate = user_input
            else:
                add_log(f"** Bad input try again.\n")
        limit_str = f"{rate}/{period}"
        is_new = True
        for i in range(len(limit_strings)):
            if period == limit_strings[i].split("/")[1]:
                limit_strings[i] = limit_str
                is_new = False
                break
        if is_new:
            limit_strings.append(limit_str)
        add_log(limit_strings)
        if len(limit_strings) < 4:
            user_select = Menu(
                ["Yes", "No"],
                "Do you want to add more limiting sting?")
            if user_select() == "No":
                break
    if len(limit_strings) > 1:
        for i in range(len(limit_strings)):
            rate_limiting_string = rate_limiting_string + limit_strings[i]
            if i < len(limit_strings)-1:
                rate_limiting_string = rate_limiting_string + ";"
    else:
        rate_limiting_string = limit_strings[0]

    with open("config.json", 'r+') as file:
        data = json.load(file)
        data["rate_limiting_string"] = rate_limiting_string
        file.seek(0)
        json.dump(data, file, indent=4)
        add_log(f"rate limiting set to -> {rate_limiting_string}")


def jwt_secret_key():
    """
        The function configure jwt secret key.
    """
    limit_strings = []
    unacceptable_secret_keys = [
        "",
        "YOURSECERTKEY-UNSAFE",
        "SECERTKEY",
        "THISISSECERTKEY",
        "THIS IS SECERT KEY",
        "THIS-IS-SECERT-KEY",
    ]
    while True:
        secret_key = None
        key_type = None
        key_type_select = Menu(
            ['Dynamic', 'Static'],
            "Please enter one of these keys type")
        key_type = key_type_select()
        if key_type == "Static":
            while secret_key is None:
                user_input = input(
                    f"Please enter a string with at least 12 characters:\n")
                if len(user_input) >= 12 and (
                        user_input.upper() not in unacceptable_secret_keys):
                    secret_key = user_input
                else:
                    add_log(f"** Weak secret key try again.\n")
        print(secret_key, key_type)
        break
    with open("config.json", 'r+') as file:
        data = json.load(file)
        is_static_secret_key = False
        if key_type == "Static":
            is_static_secret_key = True
        data["is_static_secret_key"] = is_static_secret_key
        if is_static_secret_key and secret_key is not None:
            data["static_secret_key"] = secret_key
        file.seek(0)
        json.dump(data, file, indent=4)
        add_log(
            f"JWT key type change to -> {key_type}")
        if is_static_secret_key and secret_key is not None:
            add_log(
                f"JWT secret key change to -> {secret_key}")


def check_pass_is_strong(pwd) -> bool:
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


options = [
    'Create Admin', 'Rate Limit',
    'JWT Secret Key', 'Quit'
]

action_select = Menu(
    options,
    "Please select an action to continue:"
)

result = ""
while result != "Quit":
    result = action_select()
    if result == ("Create Admin"):
        create_admin()
    elif result == ("Rate Limit"):
        rate_limit()
    elif result == ("JWT Secret Key"):
        jwt_secret_key()

quit()
