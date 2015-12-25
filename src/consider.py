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
            url = users.create_logout_url(self.request.uri)
            template_values = {
                'url': url
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
            url = users.create_login_url(self.request.uri)
            template_values = {
                'url': url
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
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is models.Instructor:
                    # Show instructor console
                    logging.info('Instructor logged in ' + str(result))
                    template_values = {'logouturl': url, 'expand': self.request.get('course')}
                    courses = models.Course.query(ancestor=result.key).fetch()
                    if courses:
                        for course in courses:
                            course.sections_all = models.Section.query(ancestor=course.key).fetch()
                            course.sections = len(course.sections_all)
                        template_values['courses'] = courses
                    template = utils.jinja_env().get_template('instructor_courses.html')
                    self.response.write(template.render(template_values))
                elif type(result) is models.Student:
                    logging.info('Student logged in ' + str(result))
                    template_values = {'logouturl': url, 'nickname': user.nickname()}
                    sections = result.sections
                    section_list = []
                    if sections:
                        for section in sections:
                            section_obj = section.get()
                            course_obj = section.parent().get()
                            if section_obj and course_obj:
                                sec = {
                                    'key': section.urlsafe(),
                                    'name': section_obj.name,
                                    'course': course_obj.name
                                }
                                section_list.append(sec)
                    template_values['sections'] = section_list
                    template = utils.jinja_env().get_template('student_home.html')
                    self.response.write(template.render(template_values))
                else:
                    logging.info(str(result) + ' navigated to Error')
                    self.redirect('/error?code=101')
            else:
                self.redirect('/error?code=101')
        else:
            self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/error', ErrorPage),
    ('/home', HomePage),
    ('/admin', admin.AdminPage),
    ('/courses', instructor.Courses),
    ('/add_section', instructor.AddSection),
    ('/toggleSection', instructor.ToggleSection),
    ('/addRound', instructor.AddRound),
    ('/activateRound', instructor.ActivateRound),
    ('/discussion', student.Discussion),
    ('/responses', instructor.Responses),
    ('/group_responses', instructor.GroupResponses),
    ('/addStudent', instructor.AddStudent),
    ('/removeStudent', instructor.RemoveStudent),
    ('/section', student.SectionPage),
    ('/groups', instructor.Groups),
    ('/rounds', instructor.Rounds),
    ('/addGroups', instructor.AddGroups),
    ('/updateGroups', instructor.UpdateGroups),
    ('/students', instructor.StudentsPage),
    ('/submitResponse', student.SubmitResponse),
])
