"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Instructor as model
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
		email = "instructor@gmail.com"
		instructor_expected = model.Instructor(email=email, is_active=True)
		instructor_expected.put();
		
		instructor_actual = instructor_expected.key.get()
		assert instructor_actual.email == email

	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties


if __name__ == '__main__':
	unittest.main()