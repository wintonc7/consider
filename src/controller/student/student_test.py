import unittest
#from google.appengine.api import memcache
#from google.appengine.ext import ndb
#from google.appengine.ext import testbed

from src import model, utils

"""Test whether an entity is stored in memcache.
If none found, check for an entity in the datastore."""
class TestStudent(model.Role.student):
    """A model class used for testing."""
    number = 1
