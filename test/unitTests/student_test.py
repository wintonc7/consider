import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed


class TestStudent(ndb.Student):
    """A student class used for testing."""
    email = ndb.StringProperty(default="dummy@gmail.com")
    preferred_email = ndb.StringProperty()
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()
