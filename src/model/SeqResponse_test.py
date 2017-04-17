"""
SeqResponse_test.py
Test classes for SeqResponse.py model. 

To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import SeqResponse as model
import unittest
from datetime import datetime

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
		index = 1
		timestamp = "2017/01/02 16:30"
		author = "student@gmail.com"
		seqresponse = model.SeqResponse(index=index, timestamp=timestamp, author=author)
		seqresponse.put();
		seqresponse = seqresponse.key.get()
		assert seqresponse.index == index
		assert seqresponse.timestamp == timestamp
		assert seqresponse.author == author		

	# TODO: Test all properties	


if __name__ == '__main__':
	unittest.main()