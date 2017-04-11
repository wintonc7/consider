"""
To run test suite, enter /model folder and run:
	> python runner.py /path/to/google_appengine
"""
import Section as model
import unittest

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed


# TODO: Refactor class structure

"""
StudentInfo
"""
class TestStudentInfo(ndb.Model):
	email = "student@gmail.com"

class ModelTestCase_StudentInfo(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestStudentInfo().put()
		self.assertEqual(1, len(TestStudentInfo.query().fetch(2)))

	def testKeyProperty(testbed):		
		email = "student@gmail.com"
		studentinfo = model.StudentInfo(email=email)
		studentinfo.put();		
		studentinfo = studentinfo.key.get()
		assert studentinfo.email == email		

"""
GraderInfo
"""
class TestGraderInfo(ndb.Model):
	email = "grader@gmail.com"

class ModelTestCase_GraderInfo(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestGraderInfo().put()
		self.assertEqual(1, len(TestGraderInfo.query().fetch(2)))

	def testKeyProperty(testbed):		
		email = "grader@gmail.com"
		graderinfo = model.GraderInfo(email=email)
		graderinfo.put();		
		graderinfo = graderinfo.key.get()
		assert graderinfo.email == email

"""
Section
"""
class TestSection(ndb.Model):	
	name = "CSE1100"

class ModelTestCase_Section(unittest.TestCase):

	def setUp(self):
		self.testbed = testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_memcache_stub()
		ndb.get_context().clear_cache()

	def tearDown(self):
		self.testbed.deactivate()

	def testInsertEntity(self):
		TestSection().put()
		self.assertEqual(1, len(TestSection.query().fetch(2)))

	def testKeyProperty(testbed):		
		name = "CSE1100"
		section = model.Section(name=name)
		section.put();		
		section = section.key.get()
		assert section.name == name
		

	# Test key as a group
	# TODO: Test Structured Property
	# TODO: Test parent-child relationships
	# TODO: Test all properties
	# TODO: Test methods


if __name__ == '__main__':
	unittest.main()