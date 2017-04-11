"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Feedback as model
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
		email = "user@gmail.com"
		other_selected = True
		feedback_text = "This is user feedback."
		feedback = model.Feedback(email=email, other_selected=other_selected, feedback=feedback_text)
		feedback.put()
		feedback = feedback.key.get()
		assert feedback.email == email
		assert feedback.other_selected == other_selected
		assert feedback.feedback == feedback_text

	# TODO: Comprehensive property test
	

if __name__ == '__main__':
	unittest.main()