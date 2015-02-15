import os
import urllib
import webapp2
import jinja2

from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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
	"""docstring for HomePage"""
	def get(self):
		
		user = users.get_current_user()

		if user:
			url = users.create_logout_url(self.request.uri)
			template_values = {
		    	'url': url
			}
			template = JINJA_ENVIRONMENT.get_template('home.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect('/');
		

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', HomePage),
], debug=True)