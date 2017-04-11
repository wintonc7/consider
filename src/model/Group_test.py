"""
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
		group_expected = model.Group(number=number)
		group_expected.put();
		
		group_actual = group_expected.key.get()
		assert group_actual.number == number

	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties


if __name__ == '__main__':
	unittest.main()