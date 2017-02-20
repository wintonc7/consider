"""
profile.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Student profile page in the app.

- Author(s): Alan Zeigler
- Last Modified: February 20, 2017

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class Profile(webapp2.RequestHandler):
    def get(self):
        """
        Displays modifiable profile options
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/')
        # end

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        students = [student]
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'nickname': student.email,
            'student': True
        }
        # Set the template html page
        template = utils.jinja_env().get_template('students/profile.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
