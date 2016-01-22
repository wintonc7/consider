"""
utils.py
~~~~~~~~~~~~~~~~~
Defines the functions and constants which are accessed by different modules of this application.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Jan. 13, 2016

--------------------


"""
import logging

from google.appengine.api import users

import models


def jinja_env():
    """
    Returns the Jinja2 environment from which templates to render the web pages can be obtained.

    """
    import jinja2
    import os
    return jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'),
            extensions=['jinja2.ext.autoescape'],
            autoescape=True)


def error_codes():
    """
    Returns a dictionary of error codes in <code: message> format.

    """
    return {
        '100': "Oops! Something went wrong please try again.",
        '101': "Sorry you are not registered with this application, please contact your instructor.",
        '102': "Sorry you are not an instructor.",
        '103': "Sorry no rounds are active for this section, please try again later.",
        '104': "Sorry the round was not found, please contact your Instructor.",
        '105': "Sorry, your group was not found, please contact your Instructor."
    }


def log(message, type='', handler=None):
    """
    Logs the message to the console using ``logging.info``.

    Args:
        message (str):
            Message to be logged.
        type (str):
            'S' for success, 'E' for error, blank for other.
        handler (webapp2.RequestHandler):
            Handler to post the same message back to the user.

    """
    logging.info(type + ' ' + message)
    if handler:
        handler.response.write(type + ' ' + message)


def error(message, handler=None):
    """
    Logs an error message to the console.

    Args:
        message (str):
          Message to be logged.
        handler (webapp2.RequestHandler):
          Handler to post the same message back to user.

    """
    log(message, type='E', handler=handler)


def get_role_user():
    """
    Returns the role and the user object for the currently logged in user.

    Returns:
        <role, user>:
            A tuple where ``role`` can be INSTRUCTOR or STUDENT
            and ``user`` is the appropriate object for the currently logged in user.

    """
    user = users.get_current_user()
    if user:
        log('Logged in: user = ' + str(user))
        if users.is_current_user_admin():
            return models.Role.admin, user
        instructor = models.Instructor.query(models.Instructor.email == user.email().lower()).get()
        if instructor:
            return models.Role.instructor, instructor
        student = models.Student.query(models.Student.email == user.email().lower()).get()
        if student:
            return models.Role.student, student
        else:
            return None, user
    else:
        log('No one logged in')
    return None, None


def get_courses_and_sections(instructor, course_name, selected_section):
    """
    Fetches the courses and sections for the given instructor.

    Args:
        instructor (object):
          Instructor whose courses are to be retrieved
        course_name (str):
          Name of the course whose sections are to be retrieved (optional)
        selected_section (str):
          Name of the selected section (optional)

    Returns:
        template_values (dict):
            Courses and sections to be rendered.

    """
    template_values = {}
    courses = models.Course.query(ancestor=instructor.key).fetch()
    if courses:
        course = None
        template_values['courses'] = courses
        if course_name:
            course_name = course_name.upper()
            course = models.Course.get_by_id(course_name, parent=instructor.key)
        if not course:
            course = courses[0]
        sections = models.Section.query(ancestor=course.key).fetch()
        template_values['selectedCourse'] = course.name
        if not sections and not course_name:
            sections = models.Section.query(ancestor=courses[0].key).fetch()
        template_values['sections'] = sections
        if sections:
            section = None
            if selected_section:
                selected_section = selected_section.upper()
                section = models.Section.get_by_id(selected_section, parent=course.key)
            if not section:
                section = sections[0]
            template_values['selectedSection'] = section.name
            template_values['selectedSectionObject'] = section
            template_values['students'] = section.students
    return template_values


def is_valid_response(response):
    """
    Checks if any of the responses is one of the three valid options: support, neutral or disagree.

    Args:
        response (list):
            A list of responses to be checked.

    Returns:
        bool:
            ``True`` if all of the responses are valid. ``False`` if any is invalid.

    """
    for i in range(1, len(response)):
        if response[i] not in ['support', 'neutral', 'disagree']:
            return False
    return True
    # SJ: 12/18/2015: Changed to make a better func. name
    # for i in range(1, len(response)):
    #     if response[i] not in ['support', 'neutral', 'disagree']:
    #         return True
    # return False
