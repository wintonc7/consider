"""
LogEntry_test.py
Test classes for LogEntry.py model. 

To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import LogEntry as model
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
		student = "student@gmail.com"
		logentry = model.LogEntry(student=student)
		logentry.put()		
		logentry = logentry.key.get()
		assert logentry.student == student

	# TODO: Test all properties


if __name__ == '__main__':
	unittest.main()