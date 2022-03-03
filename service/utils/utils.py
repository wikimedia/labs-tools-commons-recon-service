# !/usr/bin/env python3
# Authors: Eugene Egbe
# Uility functions of the reconciliation service

from urllib import response
from flask import jsonify
import json
from functools import wraps
from service.normalize.normalize import InvalidInputDataException


def catch_custom_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
    return decorated_function



def check_valid_json(obj):
    """Check for valid json object

    Args:
        obj (obj): Json input to check

    Returns:
        bool: valididty of json input
    """
    try:
        json.loads(obj)
    except ValueError:
        return False
    return True


def validate_input(input):
    """Checks for valid input provided to routes

    Args:
        input (obj): Input object

    Returns:
        object: Input object on success or failure/error on failure
    """

    result = check_valid_json(input)
    if result is False:
        raise InvalidInputDataException("Invalid input provided")
    else:
        return True


def return_invalid_input_object(e):
    """Returns a flask error object to the caller

    Args:
        e (str): Error string from the raised exception

    Returns:
        obj: flask response object of message and status code
    """
    
    return {
        "error": "error",
        "message": e.message
    }
