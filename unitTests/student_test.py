import unittest

import Student
""" from src.model import Student doesn't, work
I have tried many combinations but it won't let me go up two parent directories
since this file exists in consider/test/unittesting"""

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

"""Test whether an entity is stored in memcache.
If none found, check for an entity in the datastore."""
class TestModel(ndb.Model):
    """A model class used for testing."""
    number = ndb.IntegerProperty(default=42)
    text = ndb.StringProperty()

class TestStudent(""" Instead of ndb.Model, do src.model.Student or something"""):
    """A student class used for testing."""
    email = ndb.StringProperty()
    preferred_email = ndb.StringProperty()
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()

class StudentTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()