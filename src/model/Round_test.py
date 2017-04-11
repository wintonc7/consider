"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Round as model
import unittest

from datetime import datetime 
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


class TestQuestion(ndb.Model):
	options_total = 0
	question = "Is this a question?"

class ModelTestCase_Question(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestQuestion().put()
		self.assertEqual(1, len(TestQuestion.query().fetch(2)))

	def testKeyProperty(testbed):		
		options_total = 0
		question = "Is this a question?"
		question_expected = model.Question(options_total=options_total, question=question)
		question_expected.put();
		
		question_actual = question_expected.key.get()
		assert question_actual.options_total == options_total
		assert question_actual.question == question

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods

class TestRound(ndb.Model):	
	deadline = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")
	number = 1
	starttime = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")


class ModelTestCase_Round(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestRound().put()
		self.assertEqual(1, len(TestRound.query().fetch(2)))

	def testKeyProperty(testbed):		
		deadline = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")
		number = 1
		starttime = datetime.strptime("2017/01/02 16:30", "%Y/%m/%d %H:%M")
		response_expected = model.Round(deadline=deadline, number=number, starttime=starttime)
		response_expected.put();
		
		response_actual = response_expected.key.get()
		assert response_actual.deadline == deadline
		assert response_actual.number == number
		assert response_actual.starttime == starttime

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods


if __name__ == '__main__':
	unittest.main()