import logging
import os

import jinja2
import webapp2
from google.appengine.api import users

import admin
import instructor
import model
import student
from utils import get_role

JINJA_ENVIRONMENT = jinja2.Environment(
        # loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        loader=jinja2.FileSystemLoader('{basedir}/{srcdir}/{tempdir}'.format(basedir=os.getcwd(), srcdir='src', tempdir='templates')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

errorCodes = {
    '100': "Oops! Something went wrong please try again.",
    '101': "Sorry you are not registered with this application, please contact your Instructor.",
    '102': "Sorry you are not an instructor.",
    '103': "Sorry no rounds are active for this section, please try again later.",
    '104': "Sorry the round was not found, please contact your Instructor.",
    '105': "Sorry, your group was not found, please contact your Instructor."
}


class ErrorPage(webapp2.RequestHandler):
    """Page to display errors"""

    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            template_values = {
                'url': url
            }
            error = self.request.get('code')
            message = None
            if error:
                if error in errorCodes:
                    message = errorCodes[error]
            if not message:
                message = errorCodes['100']
            template_values['text'] = message
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/')


class MainPage(webapp2.RequestHandler):
    """Main function that will handle the first request"""

    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/home')
        else:
            url = users.create_login_url(self.request.uri)
            template_values = {
                'url': url
            }
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))


class HomePage(webapp2.RequestHandler):
    """Redirecting accordingly based on email"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is model.Instructor:
                    # Show instructor console
                    logging.info('Instructor logged in ' + str(result))
                    template_values = {'logouturl': url, 'expand': self.request.get('course')}
                    courses = model.Course.query(ancestor=result.key).fetch()
                    if courses:
                        for course in courses:
                            course.sections_all = model.Section.query(ancestor=course.key).fetch()
                            course.sections = len(course.sections_all)
                        template_values['courses'] = courses
                    template = JINJA_ENVIRONMENT.get_template('courses_and_sections.html')
                    self.response.write(template.render(template_values))
                elif type(result) is model.Student:
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
                    template = JINJA_ENVIRONMENT.get_template('student_home.html')
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
    ('/toggleInstructor', admin.AdminToggleInstructor),
    ('/add_course', instructor.AddCourse),
    ('/toggleCourse', instructor.ToggleCourse),
    ('/add_section', instructor.AddSection),
    ('/toggleSection', instructor.ToggleSection),
    ('/addRound', instructor.AddRound),
    ('/activateRound', instructor.ActivateRound),
    ('/discussion', instructor.Discussion),
    ('/responses', instructor.Responses),
    ('/group_responses', instructor.GroupResponses),
    ('/addStudent', instructor.AddStudent),
    ('/removeStudent', instructor.RemoveStudent),
    ('/section', instructor.SectionPage),
    ('/groups', instructor.Groups),
    ('/rounds', instructor.Rounds),
    ('/addGroups', instructor.AddGroups),
    ('/updateGroups', instructor.UpdateGroups),
    ('/students', student.StudentsPage),
    ('/submitResponse', student.SubmitResponse),
])
