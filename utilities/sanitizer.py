import subprocess
import bleach
from flask import jsonify, request, escape

# TODO check what to do with `cmd`
forbidden_char = ["\\", '\"', "\'", "\r", "\t", "\b", "\f", "\v",
                  "\0", "\a"]
forbidden_char2 = [";", "&", "|", "`"]


def sanitizer(input_string: str):
    """
    The function to sanitize strings for prevent injection attacks.

    Parameters:
        input_string (str): The string that will be sanitized.

    Returns:
        str: The cleaned string.
    """
    if input_string is None:
        return None
    input_string = str(input_string)
    if type(input_string) != str:
        if is_binary(input_string):
            input_string = input_string.decode()
        else:
            return str(input_string)
    for item in forbidden_char:
        if item in input_string:
            input_string = input_string.replace(item, f"\{item}")
        elif item in forbidden_char2:
            input_string = input_string.replace(item, "")
    input_string = bleach.clean(input_string).strip()
    return input_string


def is_binary(input_string):
    chars = set(input_string)
    binary_chars = {'0', '1'}
    return binary_chars == chars or chars == {'0'} or chars == {'1'}
