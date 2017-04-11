"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import ActivityLog as model
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
		assignment = ndb.Key('1', '2') # TODO: fix
		course = ndb.Key('2', '3') # TODO: fix
		log = model.ActivityLog(course=course, assignment=assignment)
		log.put()
		log = log.key.get()
		assert log.assignment == assignment
		assert log.course == course

	# TODO: Test methods
	

if __name__ == '__main__':
	unittest.main()