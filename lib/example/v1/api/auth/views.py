"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../../lib')
#from hmac_sandbox.v1.lib.user.models import User
from flask import Blueprint, jsonify, request, make_response, g
import json
import time
import logging

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """ check if the request data exists with the correct values, then check 
        if the User exists and the password matches else return 404 
    """
    if request.content_type != 'application/json' or not request.data:
        message = "Content-Type: 'application/json' required"
        logger.warn(message)
        return jsonify(message=message, success=False), 400
    for var in ['email_address', 'password']:
        if var not in request.json:
            message = "'%s' required." % var
            return jsonify(message=message, success=False), 400
    try:
        user = User(email_address=request.json['email_address'])
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return jsonify(message=message, success=False), 400
    data = g.db_client.get(user.key, quiet=True)
    if not data.success:
        logger.warn("'%s' does not exist." % request.json['email_address'])
        message = "Unknown email_address or bad password"
        return jsonify(message=message, success=False), 400
    logger.debug("'%s' successfully found!" % request.json['email_address'])
    user.set_values(values=data.value)
    if not user.check_password(request.json['password']):
        logger.warn("'%s' incorrect password" % request.json['email_address'])
        message = "Unknown email_address or bad password"
        return jsonify(message=message, success=False), 400
    message = "'%s' successfully logged in!" % request.json['email_address']
    logger.info(message)
    ## don't return hashed password
    data.value.pop('password', None)
    return jsonify(message=message, data=data.value, success=True), 200
