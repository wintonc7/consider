import os
import urllib
import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Class(ndb.Model):
	"""A main model for a particular class and root of the application"""
	name = ndb.StringProperty(required="True")
	groups = ndb.IntegerProperty(default=0, indexed=False)
	current_round = ndb.IntegerProperty(default=0, indexed=False)
	rounds = ndb.IntegerProperty(default=0, indexed=False)

class Admin(ndb.Model):
	"""A main model for representing admins"""
	email = ndb.StringProperty(required="True")

class MainPage(webapp2.RequestHandler):
	"""Main function that will handle the first request"""
	def get(self):

		user = users.get_current_user()

		if user:
			if users.is_current_user_admin():
				url = users.create_logout_url(self.request.uri)
				template_values = {
			    	'url': url
				}
				template = JINJA_ENVIRONMENT.get_template('developer.html')
				self.response.write(template.render(template_values))
			else:
				self.response.write("You are not Rohit :p")
		else:
			url = users.create_login_url(self.request.uri)
			template_values = {
		    	'url': url
			}
			template = JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render(template_values))

	def post(self):
		class_name = self.request.get('class')
		email = self.request.get('email').lower()
		
		if users.is_current_user_admin():
			newClass = Class(id=class_name)
			newClass.name = class_name
			newClass.put()

			admin = Admin(parent=newClass.key,id=email)
			admin.email = email
			admin.put()
			self.response.write(email)
		else:
			self.redirect('/');
		
application = webapp2.WSGIApplication([
    ('/secretlandingpage', MainPage),
], debug=True)