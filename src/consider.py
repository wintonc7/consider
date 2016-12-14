"""
consider.py
~~~~~~~~~~~
- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: May 30, 2016

--------------------

Main module of the app. Implements the ``application`` object; handlers for error, home and root pages; and redirects URL to appropriate handler classes.
"""

import datetime

import webapp2
from google.appengine.api import users

import config
import utils
from src import model
from .controller import admin, instructor, student, grader


class ErrorPage(webapp2.RequestHandler):
    # TODO Uniform error messaging; rethink exceptions, redirects, popups, etc.
    """
    Handles the ``/error`` page, a generic page to display errors based on app-specific, custom error code.

    The error codes are:

    * '100': "Oops! Something went wrong please try again.",
    * '101': "Sorry you are not registered with this application, please contact your Instructor.",
    * '102': "Sorry you are not an instructor.",
    * '103': "Sorry no rounds are active for this section, please try again later.",
    * '104': "Sorry the round was not found, please contact your Instructor.",
    * '105': "Sorry, your group was not found, please contact your Instructor.",
    * '106': "Sorry, you are not in a group, please contact your Instructor."

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
                'documentation': config.DOCUMENTATION,
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
            import model
            if role == model.Role.admin:
                self.redirect('/admin')
            elif role == model.Role.instructor:
                self.redirect('/courses')
            elif role == model.Role.student:
                self.redirect('/student_home')
            else:
                utils.log(str(user) + ' navigated to Error')
                self.redirect('/error?code=101')
        else:
            login_url = users.create_login_url(self.request.uri)
            template_values = {
                'loginurl': login_url,
                'documentation': config.DOCUMENTATION,
                'setup': config.SETUP_GUIDE,
                'instr_guide': config.INSTRUCTOR_GUIDE,
                'student_guide': config.STUDENT_GUIDE
            }
            template = utils.jinja_env().get_template('login.html')
            self.response.write(template.render(template_values))


class CronTask(webapp2.RequestHandler):
    def get(self):
        time_notification = 120  # Email notification when time left is no more than 2 hours
        current_time = datetime.datetime.now()
        sections = model.Section.query().fetch()
        for section in sections:
            print section.name
            num = utils.get_current_round(section)
            if num:
                rounds = model.Round.query(ancestor=section.key).fetch()
                for rnd in rounds:
                    if rnd.number == num:
                        round = rnd
                        break
                delta_time = round.deadline - current_time
                time_remaining = 24 * 60 * delta_time.days + delta_time.seconds // 60
                if 0 < time_remaining < time_notification:
                    sec_emails = [s.email for s in section.students]
                    response = model.Response.query(ancestor=round.key).fetch()
                    res_emails = [res.student for res in response]
                    to_emails = [email for email in sec_emails if email not in res_emails]
                    email_message = 'Dear Students: \n' \
                                    'No more than 30 minutes left to submit your answer.' \
                                    'Please finish it as soon as possible! \n' \
                                    'Best,\n' \
                                    'Consider Team\n'

                    utils.send_mails(to_emails, "CONSIDER: Deadline Approaching", email_message)

        self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', MainPage),  # TODO can we do away with /home?
    ('/error', ErrorPage),
    ('/admin', admin.AdminPage),
    ('/courses', instructor.Courses),
    ('/sections', instructor.Sections),
    ('/students', instructor.Students),
    ('/rounds', instructor.Rounds),
    ('/responses', instructor.Responses),
    ('/group_responses', instructor.GroupResponses),
    ('/groups', instructor.Groups),
    ('/student_home', student.HomePage),
    ('/student_rounds', student.Rounds),
    ('/crontask', CronTask),
    ('/show_responses', instructor.ShowResponses),
    ('/data_file_export', instructor.DataExport),
    ('/data_html_export', instructor.HtmlExport),
], debug=config.DEBUG)
