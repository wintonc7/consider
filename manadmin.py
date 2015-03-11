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

def class_key(class_name):
    """Constructs a Datastore key for a Admin entity.
    We use class_name as the key.
    """
    return ndb.Key('ClassName', class_name)

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
		class_name = self.request.get('class').lower()
		email = self.request.get('email').lower()
		admin = Admin(parent=class_key(class_name),id=email)

		if users.is_current_user_admin():
		    admin.email = email
		    admin.put()
		    self.response.write(email)
		else:
			self.redirect('/');
		
application = webapp2.WSGIApplication([
    ('/secretlandingpage', MainPage),
], debug=True)