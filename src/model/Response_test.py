"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Response as model
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
		comment = "This is a comment."
		student = "student@gmail.com"
		response_expected = model.Response(comment=comment, student=student)
		response_expected.put();
		
		response_actual = response_expected.key.get()
		assert response_actual.comment == comment
		assert response_actual.student == student

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods


if __name__ == '__main__':
	unittest.main()