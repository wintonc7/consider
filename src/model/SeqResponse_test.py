"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import SeqResponse as model
import unittest
from datetime import datetime

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


class TestResponse(ndb.Model):
	index = 1
	timestamp = "2017/01/02 16:30"
	author = "student@gmail.com"


class ModelTestCase(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestResponse().put()
		self.assertEqual(1, len(TestResponse.query().fetch(2)))

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

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods


if __name__ == '__main__':
	unittest.main()