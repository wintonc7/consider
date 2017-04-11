"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Round as models
import datetime
import unittest

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
	deadline = datetime.time()
	number = 1
	starttime = datetime.time()


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
	deadline = datetime.time()
	number = 1
	starttime = datetime.time()
		response_expected = model.Round(comment=comment, student=student)
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