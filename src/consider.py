"""
consider.py
~~~~~~~~~~~
- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Jan. 13, 2016

--------------------

Main module of the app. Implements the ``application`` object; handlers for error, home and root pages;
and redirects URL to appropriate handler classes.
"""

import webapp2
from google.appengine.api import users

import admin
import student
import utils
from models import Role

# Import all of the instructor controller modules
# Modify __init__.py in the Instructor directory to add or remove modules
import Instructor


class ErrorPage(webapp2.RequestHandler):
    """
    Handles the ``/error`` page, a generic page to display errors based on app-specific, custom error code.

    The error codes are:

    * '100': "Oops! Something went wrong please try again.",
    * '101': "Sorry you are not registered with this application, please contact your Instructor.",
    * '102': "Sorry you are not an instructor.",
    * '103': "Sorry no rounds are active for this section, please try again later.",
    * '104': "Sorry the round was not found, please contact your Instructor.",
    * '105': "Sorry, your group was not found, please contact your Instructor."

    HTTP errors like 404, 500 are handled by the system in the default manner.

    """

    def get(self):
        """
        If a valid ``user`` is logged in, loads the template ``error.html`` and displays the appropriate error message,
        corresponding to the error code sent in, on it. Redirects to the root page ``(/)`` otherwise.
        """
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)
            template_values = {
                'logouturl': logout_url
            }
            error = self.request.get('code')
            message = None
            if error:
                if error in utils.error_codes():
                    message = utils.error_codes()[error]
            if not message:
                message = utils.error_codes()['100']
            template_values['text'] = message
            template = utils.jinja_env().get_template('error.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/')


class MainPage(webapp2.RequestHandler):
    """
    Handles the main landing page ``(/)`` of the app. Redirects to appropriate pages based on the logged in user's role.

    If the user is logged in, and is an admin, redirects to the ``/admin`` page. If the user is an instructor,
    redirects to the ``/courses`` page. If the user is a student, redirects to the ``/student_home`` page.
    If not logged in, shows the login page.
    """

    def get(self):
        """
        The HTTP GET method on the ``MainPage``.

        Renders or redirects appropriately.
        """
        role, user = utils.get_role_user()
        if user:
            if role == Role.admin:
                self.redirect('/admin')
            elif role == Role.instructor:
                self.redirect('/courses')
            elif role == Role.student:
                self.redirect('/student_home')
            else:
                utils.log(str(user) + ' navigated to Error')
                self.redirect('/error?code=101')
        else:
            login_url = users.create_login_url(self.request.uri)
            template_values = {
                'loginurl': login_url
            }
            template = utils.jinja_env().get_template('login.html')
            self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', MainPage),
    ('/error', ErrorPage),
    ('/admin', admin.AdminPage),
    ('/courses', Instructor.courses.Courses),
    ('/sections', Instructor.sections.Sections),
    ('/students', Instructor.students.Students),
    ('/rounds', Instructor.rounds.Rounds),
    ('/test-rounds', Instructor.rounds_test.RoundsTest),
    ('/responses', Instructor.responses.Responses),
    ('/group_responses', Instructor.group_responses.GroupResponses),
    ('/groups', Instructor.groups.Groups),
    ('/student_home', student.HomePage),
    ('/student_rounds', student.Rounds),
], debug=True)
