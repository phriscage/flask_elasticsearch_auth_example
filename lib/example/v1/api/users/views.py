"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
        '/../../../../../lib')
from example.v1.lib.user import User, KEY_NAME as USER_KEY_NAME
from flask import Blueprint, jsonify, request, g
from elasticsearch import TransportError
import logging

logger = logging.getLogger(__name__)

users = Blueprint('users', __name__)

@users.route('/new', methods=['POST', 'OPTIONS'])
def create():
    """ create a user and hash their password

    **Example request:**

    .. sourcecode:: http

    GET /users/new HTTP/1.1
    Accept: application/json
    data: { 
        'email_address': 'abc@abc.com', 
        'password': 'abc123',
        'first_name': 'abc',
        'last_name': '123'
    }

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: success
    :statuscode 400: bad data
    :statuscode 409: already exists
    :statuscode 500: server error
    """
    if request.content_type != 'application/json' or not request.data:
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
    if data.get('found', None):
        message = "'%s' already exists." % user.values[USER_KEY_NAME]
        logger.warn(message)
        return jsonify(message=message, success=False), 409
    try:
        data = g.db_client.index(index='example', doc_type=user.values['_type'],
            id=user.key, body=user.values)
    except Exception as error:
        message = str(error)
        logger.warn(message)
        return jsonify(message=message, success=False), 500
    message = "'%s' added successfully!" % user.values[USER_KEY_NAME]
    logger.debug(message)
    return jsonify(message=message, success=True), 200
