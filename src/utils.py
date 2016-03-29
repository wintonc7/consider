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

from json import JSONEncoder
import datetime

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


def check_privilege(expected_role):
    """
    Checks if the currently logged in user meets the expected role passed in.

    Args:
        expected_role (object):
          The role we're checking against from the models.

    Returns:
        user (object):
          The currently logged in user object or False if user doesn't meet
          the specified role.

    """
    # First, check that the logged in user is an instructor
    role, user = get_role_user()
    if not user or role != expected_role:
        # Error if not
        if expected_role == models.Role.instructor:
            error('user is null or not Instructor')
        elif expected_role == models.Role.student:
            error('user is null or not Student')
        #end
        return False
    #end
    return user
#end

def get_current_round(section):
    """
    Fetches and returns the current round
    """
    if section.is_active:
        rounds = models.Round.query(ancestor=section.key).fetch()
        if rounds:
            for i in range(len(rounds)):
                #get start time and end time of the round
                start_time = rounds[i].starttime
                end_time = rounds[i].deadline

                #change time into a workable format
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M")

                #if the current time is inbetween the start and end time
                #return that round
                current_time = datetime.datetime.now()
                if current_time > start_time and current_time < end_time:
                    if section.current_round != rounds[i].number:
                        section.current_round = rounds[i].number
                        section.put()
                    return rounds[i].number
                #end if
            #end for
    else:
        return 0
    #end if
#end get_current_round


def get_template_all_courses_and_sections(instructor, course_name, selected_section):
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
    # First, built an empty dict to hold all the template values
    template_values = {}
    # Try and grab all the courses for this particular instructor
    courses = models.Course.query(ancestor=instructor.key).fetch()
    # Double check that this instructor actually has courses
    if courses:
        # If so, set assign that list to the template values
        course = None
        template_values['courses'] = courses
        # If a particular course name was passed in
        if course_name:
            # Convert it to upper case and try and grab it from the db
            course_name = course_name.upper()
            course = models.Course.get_by_id(course_name, parent=instructor.key)
        #end
        # If it doesn't exist, just set the active course to the first
        if not course:
            course = courses[0]
        #end
        # And set the name in the template values
        template_values['selectedCourse'] = course.name
        # Now try and grab the sections from the db
        sections = models.Section.query(ancestor=course.key).fetch()
        # If there are no sections and a course name wasn't passed in
        if not sections and not course_name:
            # Grab all sections of the "default" course
            sections = models.Section.query(ancestor=courses[0].key).fetch()
        #end
        # And add them to the template values
        template_values['sections'] = sections
        # And if there are sections
        if sections:
            section = None
            # And if a particular section name was passed in
            if selected_section:
                # Try and grab that section from the database
                selected_section = selected_section.upper()
                section = models.Section.get_by_id(selected_section, parent=course.key)
            #end
            # If it wasn't found, set a default section
            if not section:
                section = sections[0]
            #end
            # And set the rest of the template values
            template_values['selectedSection'] = section.name
            template_values['selectedSectionObject'] = section
            template_values['students'] = section.students
        #end
    #end
    # And finally return the template values
    return template_values
#end get_template_all_courses_and_sections


def get_course_and_section_objs(page_handler, instructor):
    """
    Given the page handler and the currently logged in instructor, returns the
    course and section objects from the database from their keys on the page.

    Args:
        page_handler (webapp2.RequestHandler object):
          The current request handler for the page the instructor is on.
        instructor (object):
          The currently logged in instructor object.

    Returns:
        <course, section>:
          A tuple where the course and section object have been retrieved from
          the database given their id keys from the request handler.

    """
    # First, grab the course and section from the page
    course_name = page_handler.get('course').upper()
    section_name = page_handler.get('section').upper()
    # And set the course and section to null
    course, section = None, None

    # Check that we actually get them
    if not course_name or not section_name:
        # Error if not
        error('Invalid arguments: course_name or section_name is null', handler=page_handler)
    else:
        # Now grab the course from the database
        course = models.Course.get_by_id(course_name, parent=instructor.key)
        # And check that it actually exists
        if not course:
            # Error if not
            error('Course {c} does not exist!'.format(c=course_name), handler=page_handler)
        else:
            # Now grab the section from the database
            section = models.Section.get_by_id(section_name, parent=course.key)
            # And check that it actually exists
            if not section:
                # Error if not
                error('Section {s} does not exist!'.format(s=section_name), handler=page_handler)
            #end
        #end
    #end
    # And finally return the course and section
    return course, section
#end get_course_and_section_objs

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


def convert_time(old_time):
    """
    Provides a method to switch between isoformat date-time string (used in
    the database and for deadline checking in the views) and python datetime
    objects used to manipulate and compare times.

    Args:
        old_time (object):
            Either an isoformat string or a python datetime object.

    Returns:
        isoformat string or python datetime object (opposite of input)
    """
    new_time = None

    # Check if the input time is a datetime object or string
    if type(old_time) is datetime.datetime:
        # If so, convert it to iso format the strip the last three characters
        # since we're not storing seconds in the database
        new_time = old_time.isoformat()[:-3]
    else:
        # Ohterwise, we were given a iso string from the database
        # So, use datetime to convert it to an object
        new_time = datetime.datetime.strptime(old_time, "%Y-%m-%dT%H:%M")
    #end
    return new_time
#end


# Simple class to serialize Round objects
class RoundEncoder(JSONEncoder):
    def default(self, obj):
        json_round = dict()
        json_round['deadline'] = obj.deadline
        json_round['number'] = obj.number
        json_round['description'] = obj.description
        json_round['is_anonymous'] = obj.is_anonymous
        json_round['is_quiz'] = obj.is_quiz
        json_round['starttime'] = obj.starttime
        return json_round
    #end
#end