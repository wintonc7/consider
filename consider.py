import os
import urllib
import webapp2
import jinja2
import logging

from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def class_key(class_name):
    """Constructs a Datastore key for a Admin entity.
    We use class_name as the key.
    """
    return ndb.Key('ClassName', class_name)

class Admin(ndb.Model):
	"""A main model for representing admins"""
	email = ndb.StringProperty(required="True")

class Student(ndb.Model):
	"""A student model for all the students"""
	email = ndb.StringProperty(required="True")
	class_name = ndb.StringProperty(required="True")

class MainPage(webapp2.RequestHandler):
	"""Main function that will handle the first request"""
	def get(self):

		user = users.get_current_user()

		if user:
			self.redirect('/home');
		else:
			url = users.create_login_url(self.request.uri)
			template_values = {
		    	'url': url
			}
			template = JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render(template_values))

class HomePage(webapp2.RequestHandler):
	"""Handling answer input"""
	def get(self):
		
		user = users.get_current_user()

		if user:
			result = Admin.query(Admin.email == user.email()).get()

			if result:
				logging.info('Admin logged in ' + str(result))
				section = str(result.key.parent().string_id())

				url = users.create_logout_url(self.request.uri)
				template_values = {
			    	'logouturl': url,
			    	'section': section
				}
				template = JINJA_ENVIRONMENT.get_template('admin.html')
				self.response.write(template.render(template_values))
			else:
				result = Student.query(Student.email == user.email()).get()

				if result:
					logging.info('Student logged in ' + str(result))
					url = users.create_logout_url(self.request.uri)
					template_values = {
				    	'url': url
					}
					template = JINJA_ENVIRONMENT.get_template('home.html')
					self.response.write(template.render(template_values))
				else:
					self.response.write("Sorry you are not yet registered with this application, please contact your professor.")
		else:
			self.redirect('/');

	def post(self):
		self.response.write("Got it!");

class AddStudent(webapp2.RequestHandler):
	"""Adding students to the database"""
	def post(self):

		user = users.get_current_user()

		if user:
			result = Admin.query(Admin.email == user.email()).get()

			if result:
				class_name = self.request.get('class').lower()
				email = self.request.get('email').lower()
				student = Student(parent=result.key, id = email)
				student.email = email
				student.class_name = class_name
				student.put()
				self.response.write(email)
			else:
				self.redirect('/');
		else:
			self.redirect('/');		

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', HomePage),
    ('/addStudent', AddStudent),
], debug=True)