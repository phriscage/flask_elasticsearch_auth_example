"""
    user.py
"""
from __future__ import absolute_import
import time
import re
import logging
from werkzeug.security import generate_password_hash, check_password_hash

KEY_NAME = 'email_address'
#REQUIRED_ARGS = (KEY_NAME, 'password',)
REQUIRED_ARGS = (KEY_NAME,)
VALID_ARGS = REQUIRED_ARGS + ('first_name', 'last_name',)
EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

logger = logging.getLogger(__name__)

class User(object):
    """ encapsulate the user as an object """

    def __init__(self, **kwargs):
        """ instantiate the class """
        self.key = None
        self.values = {}
        self._validate_args(**kwargs)
        self._set_key(kwargs[KEY_NAME])
        self._set_values()

    def _validate_args(self, **kwargs):
        """ validate the model args """
        logger.debug("Validating args...")
        for arg in VALID_ARGS:
            if arg in REQUIRED_ARGS and not kwargs.get(arg, None):
                message = "'%s' is required." % arg
                logger.warn(message)
                raise ValueError(message)
            if kwargs.has_key(arg):
                self.values[arg] = kwargs.get(arg)
        ## argument specific requirements
        if not EMAIL_REGEX.match(kwargs[KEY_NAME]):
            message = ("'%s' is not valid '%s'." % (kwargs[KEY_NAME], KEY_NAME))
            raise ValueError(message)
        if kwargs.get('password', None):
            # self._validate_password(str(kwargs['password']))
            self.set_password(str(kwargs['password']))

    def _set_key(self, value):
        """ set the key value """
        self.key = '%s' % value
        logger.debug("'%s' key set.", self.key)

    def _set_values(self):
        """ set the default values """
        self.set_values()

    def set_values(self, values=None):
        """ set the model attributes and default values """
        logger.debug("Setting attributes...")
        if not values:
            self.values['_type'] = self.__class__.__name__.lower()
            self.values['is_active'] = True
            self.values['created_at'] = time.time()
        else:
            self.values = values

    def set_password(self, password):
        """ set the password using werkzeug generate_password_hash """
        self.values['password'] = generate_password_hash(password)

    def check_password(self, password):
        """ check the password using werkzeug check_password_hash """
        if not self.values.get('password', None):
            return None
        return check_password_hash(self.values['password'], password)

    def is_authenticated(self):
        """ should just return True unless the object represents a user
            that should not be allowed to authenticate for some reason.
        """
        if self.is_anonymous():
            return False
        return True

    def is_active(self):
        """ method should return True for users unless they are inactive, for
            example because they have been banned.
        """
        if not self.values.get('is_active', False):
            return False
        return True

    def is_anonymous(self):
        """ method should return True only for fake users that are not supposed
            to log in to the system.
        """
        if not self.values.get('is_anonymous', False):
            return False
        return True

    def get_id(self):
        """ return the self.key """
        return self.values[KEY_NAME]
