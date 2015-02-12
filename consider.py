import webapp2

class MainPage(webapp2.RequestHandler):
	"""docstring for MainPage"""
	def get(self):
		self.response.write('Hello Rohit!')


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)