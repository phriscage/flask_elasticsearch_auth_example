#!/usr/bin/env python
"""
API bootstrap file
"""
import os
import sys
import argparse
import logging
from flask import Flask, jsonify, g
from flask.ext.login import LoginManager, current_user
from elasticsearch import Elasticsearch

sys.path.insert(0, os.path.dirname(
    os.path.realpath(__file__)) + '/../../../../lib')

from example.v1.lib.user import User

APP_SECRET_KEY = os.urandom(32)

logger = logging.getLogger(__name__)

login_manager = LoginManager()

#ELASTICSEARCH_HOST = '127.0.0.1'
#ELASTICSEARCH_PORT = 9200

@login_manager.user_loader
def load_user(email_address):
    try:
        user = User(email_address=email_address)
    except ValueError as error:
        message = str(error)
        logger.warn(message)
        return None
    data = {}
    try:
        data = g.db_client.get('example', user.key)
    except (TransportError, Exception) as error:
        if not getattr(error, 'status_code', None) == 404:
            logger.critical(str(error))
            return None
    if not data.get('found', None):
        message = "'%s' does not exist." % email_address
        logger.warn(message)
        return None
    user.set_values(values=data['_source'])
    return user


def connect_db():
    """ connect to couchbase """
    try:
        db_client = Elasticsearch()
            #[{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT}],
            #use_ssl=True,)
            #sniff_on_connection_fail=True,)
    except Exception as error:
        logger.critical(error)
        raise
    return db_client


def create_app():
    """ dynamically create the app """
    #app = Flask(__name__, static_url_path='')
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.secret_key = APP_SECRET_KEY
    login_manager.init_app(app)

    @app.before_request
    def before_request():
        """ create the db_client global if it does not exist """
        if not hasattr(g, 'db_client'):
            g.db_client = connect_db()
        if not hasattr(g, 'user'):
            g.user = current_user


    def default_error_handle(error=None):
        """ create a default json error handle """
        return jsonify(error=str(error), message=error.description,
                    success=False), error.code

    ## handle all errors with json output
    for error in range(400, 420) + range(500, 506):
        app.error_handler_spec[None][error] = default_error_handle

    ## add each api Blueprint and create the base route
    from example.v1.api.auth.views import auth
    app.register_blueprint(auth, url_prefix="/v1/auth")
    from example.v1.api.users.views import users
    app.register_blueprint(users, url_prefix="/v1/users")
    from example.v1.api.test.views import test
    app.register_blueprint(test, url_prefix="/v1/test")

    return app


def bootstrap(**kwargs):
    """bootstraps the application. can handle setup here"""
    app = create_app()
    app.debug = True
    app.run(host=kwargs['host'], port=kwargs['port'])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format=("%(asctime)s %(levelname)s %(name)s[%(process)s] : %(funcName)s"
                " : %(message)s"),
        #filename='/var/log/AAA/%s.log' % FILE_NAME
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname or IP address", dest="host",
                        type=str, default='0.0.0.0')
    parser.add_argument("--port", help="Port number", dest="port", type=int,
                        default=8000)
    args = parser.parse_args()
    bootstrap(**args.__dict__)
