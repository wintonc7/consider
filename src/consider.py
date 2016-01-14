"""
consider.py
~~~~~~~~~~~
- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 18, 2015

--------------------

Main module of the app. Implements the ``application`` object; handlers for error, home and root pages; and redirects URL to appropriate handler classes.
"""

import logging

import webapp2
from google.appengine.api import users

import admin
import instructor
import models
import student
import utils


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
    Handles the main landing page ``(/)`` of the app.

    If the user is authenticated successfully, redirects to the ``/home`` page, otherwise to the ``login`` page.
    """

    def get(self):
        """
        The HTTP GET method on the ``MainPage``.

        Renders or redirects appropriately.
        """
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.redirect('/admin')
            else:
                self.redirect('/home')
        else:
            login_url = users.create_login_url(self.request.uri)
            template_values = {
                'url': login_url
            }
            template = utils.jinja_env().get_template('login.html')
            self.response.write(template.render(template_values))


class HomePage(webapp2.RequestHandler):
    """
    Handles the ``/home`` page. Redirects based on the *role* of the user (Instructor or Student).
    """

    def get(self):
        """
        If a valid ``user`` is logged in, and if the user is an ``Instructor``, redirect to the Instructor console, which contains a list of courses and sections that instructor is in charge of; if the user is a ``Student``, retrieves the list of sections that student is enrolled in, and redirects to the student home page populated with that list.
        """
        role, user = utils.get_role_user()
        if role and user:
            logging.info(role + ' logged in: ' + str(user))
            self.redirect('/courses') if role == models.Role.instructor else  self.redirect('/student_home')
        else:
            self.redirect('/error?code=101')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/error', ErrorPage),
    ('/home', HomePage),
    ('/admin', admin.AdminPage),
    ('/courses', instructor.Courses),
    ('/sections', instructor.Section),
    ('/students', instructor.Students),
    ('/rounds', instructor.Rounds),
<<<<<<< HEAD
=======
    ('/discussion', student.Discussion),
>>>>>>> origin/master
    ('/responses', instructor.Responses),
    ('/group_responses', instructor.GroupResponses),
    ('/groups', instructor.Groups),
<<<<<<< HEAD
    ('/discussion', student.Discussion),
    ('/student_home', student.HomePage),
    ('/student_rounds', student.Rounds),
], debug=True)
=======
    ('/addGroups', instructor.AddGroups),
    ('/updateGroups', instructor.UpdateGroups),
    ('/submitResponse', student.SubmitResponse),
])
>>>>>>> origin/master
