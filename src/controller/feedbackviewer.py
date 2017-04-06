"""
feedbackviewer.py
~~~~~~~~~~~~~~~~~

- Author(s): Daniel Stelsson
- Last Modified: April 6, 2017

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class ViewFeedBackPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        logout_url = users.create_logout_url(self.request.uri)
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url
        }
        # Set the template html page
        template = utils.jinja_env().get_template('view_feedback.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
    def post(self):
       i = "placeholder"
