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

def quiz_key(class_name, quiz_number):
    """Constructs a Datastore key for a Response entity.
    We use class_name and quiz number as the keys.
    """
    return ndb.Key('ClassName', class_name, 'QuizNumber', quiz_number)

class Admin(ndb.Model):
	"""A main model for representing admins"""
	email = ndb.StringProperty(required="True")

class Student(ndb.Model):
	"""A student model for all the students"""
	email = ndb.StringProperty(required="True")
	class_name = ndb.StringProperty(required="True")

class Response(ndb.Model):
	"""A response model for all the answers"""
	option = ndb.StringProperty(required="True")
	comment = ndb.StringProperty(required="True")
	student = ndb.StringProperty(required="True")

class MainPage(webapp2.RequestHandler):
	"""Main function that will handle the first request"""
	def get(self):

		user = users.get_current_user()

		if user:
			self.redirect('/home')
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
			url = users.create_logout_url(self.request.uri)

			if result:
				logging.info('Admin logged in ' + str(result))
				section = str(result.key.parent().string_id())

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
					response = Response.get_by_id(result.email, parent=quiz_key(result.class_name,1))
					logging.info(str(response))
					if response:	
						template_values = {
					    	'url': url,
					    	'option':response.option,
					    	'comment':response.comment
						}
					else:
						template_values = {
					    	'url': url
						}
					template = JINJA_ENVIRONMENT.get_template('home.html')
					self.response.write(template.render(template_values))
				else:
					self.response.write("Sorry you are not yet registered with this application, please contact your professor. <a href='"+url+"'>Logout</a>")
		else:
			self.redirect('/')

	def post(self):
		
		user = users.get_current_user()

		if user:
			student = Student.query(Student.email == user.email()).get()

			if student:
				option = self.request.get('option').lower()
				comment = self.request.get('comm')
				if(not (option and comment)):
					self.response.write('Sorry! There was some error submitting your response please try again later.')
				else:
					response = Response(parent=quiz_key(student.class_name,1), id=student.email)
					response.option = option
					response.comment = comment
					response.student = student.email
					response.put()
					logging.info('Response saved from ' + str(student.email) + ', opt: '+ str(option)+ ', comment: '+ str(comment))
					self.response.write('Thank you, your response have been saved and you can edit your response any time before the deadline.')
			else:
				self.redirect('/')
		else:
			self.redirect('/')

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
				self.redirect('/')
		else:
			self.redirect('/')	

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', HomePage),
    ('/addStudent', AddStudent),
], debug=True)