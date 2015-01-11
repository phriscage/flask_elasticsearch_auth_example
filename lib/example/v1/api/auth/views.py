"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
                '/../../../../../lib')
from example.v1.lib.user import User
from flask import Blueprint, jsonify, request, g, session
from flask.ext.login import login_user, current_user, logout_user
from elasticsearch import TransportError
import logging

logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    """ check if the user exists and verify if their password is correct

    **Example request:**

    .. sourcecode:: http

    GET /users/new HTTP/1.1
    Accept: application/json
    data: {
        'email_address': 'abc@abc.com',
        'password': 'abc123',
        'name': 'abc'
    }

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: success
    :statuscode 400: bad data
    :statuscode 500: server error
    """
    if not request.json:
        message = "Content-Type: 'application/json' required"
        logger.warn(message)
        return jsonify(message=message, success=False), 400
    try:
        user = User(**request.json)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return jsonify(message=message, success=False), 400
    data = {}
    try:
        data = g.db_client.get('example', user.key)
    except (TransportError, Exception) as error:
        if not getattr(error, 'status_code', None) == 404:
            logger.critical(str(error))
            message = "Something broke... We are looking into it!"
            return jsonify(message=message, success=False), 500
    if not data.get('found', None):
        logger.warn("'%s' does not exist.", request.json['email_address'])
        message = "Unknown email_address or bad password"
        return jsonify(message=message, success=False), 400
    logger.debug("'%s' successfully found!", request.json['email_address'])
    user.set_values(values=data['_source'])
    if not user.check_password(request.json['password']):
        logger.warn("'%s' incorrect password", request.json['email_address'])
        message = "Unknown email_address or bad password"
        return jsonify(message=message, success=False), 400
    login_user(user)
    message = "'%s' successfully logged in!" % request.json['email_address']
    logger.info(message)
    ## don't return hashed password
    del data['_source']['password']
    return jsonify(message=message, data=data, success=True), 200

@auth.route('/logout')
def logout():
    """ logout the user and redirect to home """
    logout_user()
    logger.debug("logging out: '%s'", request)
    message = "Successfully logged out. See you soon!"
    return jsonify(message=message, success=True), 200
