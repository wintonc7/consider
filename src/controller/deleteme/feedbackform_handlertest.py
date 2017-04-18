from google.appengine.api import memcache
from google.appengine.ext import testbed
import webapp2
import webtest

import feedbackform as model

class AppTest(unittest.TestCase):

	def setUp(self):
	    app = webapp2.WSGIApplication([('/feedbackform/', FeedbackForm)])
	    self.testapp = webtest.TestApp(app)
	    self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

 	def tearDown(self):
    	self.testbed.deactivate()

  	"""def testFeedbackFormHandler_post_isStudent(self):
	    # First define a key and value to be cached.
	    is_student = True
	    email = 'student@gmail.com'
	    tags = 'tag1,tag2,tag3'
	    otherTag = 'otherTag'
	    comments = 'This is a comment'

	 	# Test redirector
	"""
	
	def testFeedbackFormHandler_get(self):
		response = self.testapp.get('/')
		self.assertEqual(response.status_int, 200)
		self.assertEqual(response.normal_body, )
		self.assertEqual(response.content_type, 'text/plain')

