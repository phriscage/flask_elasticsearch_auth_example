"""
    user.py
"""
from __future__ import absolute_import
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + 
    '/../../../../lib')
import time
import re
import logging
from werkzeug import generate_password_hash, check_password_hash


EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')
REQUIRED_ARGS = ('db_client', 'email_address')
KEY_NAME = 'email_address'

logger = logging.getLogger(__name__)

class User(object):
    """ encapsulate the user as an object """
    
    def __init__(self, **kwargs):
        """ instantiate the class """
        self.key = None
        self.values = {}
        self.db_client = None
        self._validate_args(**kwargs)
        self.set_key(self.__class__.__name__.lower(), kwargs[KEY_NAME])
        self.current_time = time.time()

    def _validate_args(self, **kwargs):
        """ validate the model args """
        logger.debug("Validating args...")
        for req_arg in REQUIRED_ARGS:
            if not kwargs.has_key(req_arg):
                message = "'%s' is missing." % req_arg
                logger.warn(message)
                raise ValueError(message)
            if req_arg in ['db_client']:
                setattr(self, req_arg, kwargs.get(req_arg))
            else:
                self.values[req_arg] = kwargs.get(req_arg)
        ## argument specific requirements
        if not EMAIL_REGEX.match(kwargs[KEY_NAME]):
            message = ("'%s' is not valid '%s'." % (kwargs[KEY_NAME], KEY_NAME))
            raise ValueError(message)
        if kwargs.has_key('password'):
            # self._validate_password(str(kwargs['password']))
            self.set_password(str(kwargs['password']))

    def set_key(self, attr, value):
        """ set the key value """
        self.key = '%s::%s' % (attr, value)
        logger.debug("'%s' key set." % self.key)

    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            self.values['created_at'] = self.current_time
        else:
            self.values = values
        
    def set_password(self, password):
        """ set the password using werkzeug generate_password_hash """
        self.values['password'] = generate_password_hash(password)

    def check_password(self, password):
        """ check the password using werkzeug check_password_hash """
        if not self.values.get('password') or not self.values['password']:
            return None
        return check_password_hash(self.values['password'], password)

    def is_authenticated(self):
        """ should just return True unless the object represents a user
            that should not be allowed to authenticate for some reason.
        """
        return True

    def is_active(self):
        """ method should return True for users unless they are inactive, for
            example because they have been banned.
        """
        return True

    def is_anonymous(self):
        """ method should return True only for fake users that are not supposed
            to log in to the system.
        """
        return False

    def get_id(self):
        """ return the self.key """
        return self.values[KEY_NAME]

    def add(self):
        """ add the elasticsearch document and/or children """
        logger.info("Adding the document for key: '%s'" % self.key)
        try:
            data = self.db_client.add(self.key, self.values)
        except KeyExistsError as error:
            logger.warn(error)
            raise
        return data
