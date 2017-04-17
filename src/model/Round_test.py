"""
Round_test.py
Test classes for Round.py model. 

To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Round as model
import unittest

from datetime import datetime 
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


class ModelTestCase_Question(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testKeyProperty(testbed):		
		options_total = 0
		questionText = "Is this a question?"
		question = model.Question(options_total=options_total, question=questionText)
		question.put();		
		question = question.key.get()
		assert question.options_total == options_total
		assert question.question == questionText

	# Test key as a group	
	# TODO: Test all properties

class ModelTestCase_Round(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testKeyProperty(testbed):		
		deadline = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")
		number = 1
		starttime = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")
		response = model.Round(deadline=deadline, number=number, starttime=starttime)
		response.put();
		
		response = response.key.get()
		assert response.deadline == deadline
		assert response.number == number
		assert response.starttime == starttime

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods


if __name__ == '__main__':
	unittest.main()