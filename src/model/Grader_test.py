"""
Grader_test.py
Test classes for Grader.py model. 

To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Grader as model
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
		email = "grader@gmail.com"
		grader = model.Grader(email=email, is_active=True)
		grader.put();		
		grader = grader.key.get()
		assert grader.email == email	

	# Test all properties


if __name__ == '__main__':
	unittest.main()