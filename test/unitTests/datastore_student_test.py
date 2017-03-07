import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class TestStudent(ndb.Student):
    """A student class used for testing."""
