"""
activitylog.py
~~~~~~~~~~~~~~~~~
Implements the APIs for the Student activity log in the app.

- Author(s): Alan Zeigler
- Last Modified: March 5, 2017

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class ActivityLog(webapp2.RequestHandler):
    def get(self):
        """
        Obtains all relevant log entries for the logged in student
        """

        # First, check that logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            #Redirect home if not a student
            return self.redirect('/')
        # end

        # Use obtained user object to obtain relevant log entries

        # Format log entries as JSON and export

        # end get