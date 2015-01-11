"""
    views file contains all the routes for the app and maps them to a
    specific hanlders function.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) +
                '/../../../../../lib')
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required
import logging

logger = logging.getLogger(__name__)

test = Blueprint('test', __name__)

@test.route('')
@login_required
def index():
    """ return the test cookie for a logged-in user

    **Example request:**

    .. sourcecode:: http

    GET /test HTTP/1.1
    Accept: */*

    **Example response:**

    .. sourcecode:: http

    HTTP/1.1 200 OK
    Content-Type: application/json

    :statuscode 200: success
    :statuscode 400: bad data
    :statuscode 500: server error
    """
    data = { 'cookies': request.cookies }
    message = "Test"
    logger.info(message)
    return jsonify(message=message, data=data, success=True), 200
