"""
Group.py
Test classes for Group.py model. 

To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Group as model
import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


class ModelTestCase(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testKeyProperty(testbed):		
		number = 12345
		group = model.Group(number=number)
		group.put();		
		group = group.key.get()
		assert group.number == number

	# TODO: Test all properties
	# TODO: Test parent-child relationships


if __name__ == '__main__':
	unittest.main()