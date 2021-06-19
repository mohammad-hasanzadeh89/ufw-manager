import os
import sys
import getopt
import re
import getpass
import sqlite3
import bcrypt

from utilities.sanitizer import sanitizer
from utilities.logger import add_log


def help():
    print("Diplaying Help")


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

# TODO change rate limiting


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


# Remove 1st argument from the
argument_list = sys.argv[1:]
argument_list = [item.lower() for item in argument_list]

options = ['help', 'create_admin', ]
try:
    arguments, values = getopt.getopt(argument_list, [], options)

    for arg, value in arguments:
        if arg == ("--help"):
            help()
        elif arg == ("--create_admin"):
            create_admin()
        else:
            help()
except getopt.error as err:
    add_log(err)
