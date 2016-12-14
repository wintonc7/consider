"""
utils.py
~~~~~~~~~~~~~~~~~
Defines the functions and constants which are accessed by different modules of this application.

- Author(s): Rohit Kapoor, Swaroop Joshi, Dustin Stanley
- Last Modified: May 30, 2016

--------------------


"""
import datetime
import logging
from json import JSONEncoder

from google.appengine.api import mail
from google.appengine.api import users

import model


class Local_TZ(object):
    """
    Handles conversions to and from UTC, allowing for support
    for the times and dates to be displayed in the local timezone
    for the application.
    """

    @staticmethod
    def to_utc(dt):
        return dt - Local_TZ.utcoffset(dt)
        # end .to_utc()

    @staticmethod
    def from_utc(dt):
        return dt + Local_TZ.utcoffset(dt)
        # end .from_utc()

    @staticmethod
    def utcoffset(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        return datetime.timedelta(hours=-5) + Local_TZ.dst(dt)
        # end .utcoffset()

    @staticmethod
    def dst(dt=None):
        if dt is None:
            # Default to the current time.
            dt = datetime.datetime.now()

        # 2 am on the second Sunday in March
        dst_start = Local_TZ.FirstSunday(datetime.datetime(dt.year, 3, 8, 2))
        # 1 am on the first Sunday in November
        dst_end = Local_TZ.FirstSunday(datetime.datetime(dt.year, 11, 1, 1))

        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(hours=0)
            # end .dst()

    @staticmethod
    def FirstSunday(dt):
        """First Sunday on or after dt."""
        return dt + datetime.timedelta(days=(6 - dt.weekday()))
        # end .FirstSunday()

    @staticmethod
    def tzname(dt=None):
        if dt is None:
            dt = datetime.datetime.now()
        if Local_TZ.dst(dt) == datetime.timedelta(hours=0):
            return "EST"
        else:
            return "EDT"
            # end .tzname()


# end Local_TZ() class definition.


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
        '105': "Sorry, your group was not found, please contact your Instructor.",
        '106': "Sorry, you are not in a group, please contact your Instructor."
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
    log(message, type='E', handler=handler)  # FIXME: E vs Error!


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
            return model.Role.admin, user
        instructor = model.Instructor.query(
            model.Instructor.email == user.email().lower()).get()
        if instructor:
            return model.Role.instructor, instructor
        student = model.Student.query(model.Student.email == user.email().lower()).get()
        if student:
            return model.Role.student, student
        grader = model.Grader.query(model.Grader.email == user.email().lower()).get()
        if grader:
            return model.Role.grader, grader
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
          The role we're checking against from the

    Returns:
        user (object):
          The currently logged in user object or False if user doesn't meet
          the specified role.

    """
    # First, check that the logged in user is an instructor
    role, user = get_role_user()
    if not user or role != expected_role:
        # Error if not
        if expected_role == model.Role.instructor:
            error('user is null or not Instructor')
        elif expected_role == model.Role.student:
            error('user is null or not Student')
        # end
        return False
    # end
    return user


# end

def get_current_round(section):
    """
    Fetches and returns the current round
    """
    # Check that the rounds for this section have actually started
    if section.current_round != 0:
        rounds = model.Round.query(ancestor=section.key).fetch()
        if rounds:
            for i in range(len(rounds)):
                # get start time and end time of the round
                start_time = rounds[i].starttime
                end_time = rounds[i].deadline

                # change time into a workable format
                # start_time = conveget_current_round_object_time(end_time)

                # if the current time is inbetween the start and end time
                # return that round
                current_time = datetime.datetime.now()
                if start_time < current_time < end_time:
                    if section.current_round != rounds[i].number:
                        section.current_round = rounds[i].number
                        section.put()
                    return rounds[i].number
                    # end if
                    # end for
    else:
        return 0
        # end if


# end get_current_round

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
    courses = model.Course.query(ancestor=instructor.key).fetch()
    # Double check that this instructor actually has courses
    if courses:
        # If so, set assign that list to the template values
        course = None
        template_values['courses'] = courses
        # If a particular course name was passed in
        if course_name:
            # Convert it to upper case and try and grab it from the db
            course_name = course_name.upper()
            course = model.Course.get_by_id(course_name, parent=instructor.key)
        # end
        # If it doesn't exist, just set the active course to the first
        if not course:
            course = courses[0]
        # end
        # And set the name in the template values
        template_values['selectedCourse'] = course.name
        # Now try and grab the sections from the db
        sections = model.Section.query(ancestor=course.key).fetch()
        # If there are no sections and a course name wasn't passed in
        if not sections and not course_name:
            # Grab all sections of the "default" course
            sections = model.Section.query(ancestor=courses[0].key).fetch()
        # end
        # And add them to the template values
        template_values['sections'] = sections
        # And if there are sections
        if sections:
            section = None
            # And if a particular section name was passed in
            if selected_section:
                # Try and grab that section from the database
                selected_section = selected_section.upper()
                section = model.Section.get_by_id(selected_section, parent=course.key)
            # end
            # If it wasn't found, set a default section
            if not section:
                section = sections[0]
            # end
            # And set the rest of the template values
            template_values['selectedSection'] = section.name
            template_values['selectedSectionObject'] = section
            if section.students:
                template_values['students'] = section.students
                # end
    # end
    # And finally return the template values
    return template_values


# end get_template_all_courses_and_sections

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
        course = model.Course.get_by_id(course_name, parent=instructor.key)
        # And check that it actually exists
        if not course:
            # Error if not
            error('Course {c} does not exist!'.format(c=course_name), handler=page_handler)
        else:
            # Now grab the section from the database
            section = model.Section.get_by_id(section_name, parent=course.key)
            # And check that it actually exists
            if not section:
                # Error if not
                error('Section {s} does not exist!'.format(s=section_name), handler=page_handler)
                # end
                # end
    # end
    # And finally return the course and section
    return course, section


# end get_course_and_section_objs

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
    if type(old_time) == datetime.datetime:
        # If so, convert it to iso format the strip the last three characters
        # since we're not storing seconds in the database
        new_time = old_time.isoformat()[:-3]
    else:
        # Ohterwise, we were given a iso string from the database
        # So, use datetime to convert it to an object
        if (len(old_time.split(":")) == 2):
            new_time = datetime.datetime.strptime(old_time, "%Y-%m-%dT%H:%M")
        else:
            new_time = datetime.datetime.strptime(old_time, "%Y-%m-%dT%H:%M:%S.%f")
    # end
    return new_time


# end convert_time


def send_mail(senders_email, section, subject, message):
    """
    Given the senders email(instructor) and the section object,
    send an email to all students in the section from the instructor.

    Args:
        senders_email:
            The instructor currently logged in.
        section (object):
            The section to send the emails to.
        subject (string):
            The subject line of the email.
        message (string):
            The body of the email.
    """

    # Default messages
    email_subject = "Consider Assignment"
    email_message = "The rounds have started"

    # Grab all the student emails from the section object
    recipient_emails = [s.email for s in section.students]
    # Subject of the email
    if subject:
        email_subject = subject
    # Message to be sent to the students via email
    if message:
        email_message = message
    # Send the email to the list of email addresses
    # senders_email='kaichen547@gmail.com'
    for email in recipient_emails:
        mail.send_mail(sender=senders_email,
                       to=email,
                       subject=email_subject,
                       body=email_message)


def get_student_info(email, students):
    for student_info in students:
        if student_info.email == email:
            return student_info
    return None


def get_grader_info(email, graders):
    for grader_info in graders:
        if grader_info.email == email:
            return grader_info
    return None

# end


def get_current_round_object(section):
    """
    Fetches and returns the current round
    """
    # Check that the rounds for this section have actually started
    if section.current_round != 0:
        rounds = model.Round.query(ancestor=section.key).fetch()
        if rounds:
            for i in range(len(rounds)):
                # get start time and end time of the round
                start_time = rounds[i].starttime
                end_time = rounds[i].deadline

                # change time into a workable format
                start_time = start_time
                end_time = end_time

                # if the current time is inbetween the start and end time
                # return that round
                current_time = datetime.datetime.now()
                if start_time < current_time < end_time:
                    if section.current_round != rounds[i].number:
                        section.current_round = rounds[i].number
                        section.put()
                    return rounds[i]
                    # end if
                    # end for
    else:
        return None
        # end if


# end get_current_round_object

def get_next_round_object(section):
    """
    Fetches and returns the current round
    """
    # Check that the rounds for this section have actually started
    if section.current_round != 0:
        rounds = model.Round.query(ancestor=section.key).fetch()
        if rounds:
            for i in range(len(rounds) - 1):
                # get start time and end time of the round
                start_time = rounds[i].starttime
                end_time = rounds[i].deadline

                start_time = start_time
                end_time = end_time

                # if the current time is inbetween the start and end time
                # return that round
                current_time = datetime.datetime.now()
                if current_time > start_time and current_time < end_time:
                    if section.current_round != rounds[i].number:
                        section.current_round = rounds[i].number
                        section.put()
                    return rounds[i + 1]
                    # end if
                    # end for
    else:
        return None
        # end if


# end get_next_round_object

def str_to_datetime(dt):
    """
    Converts the input string (in %Y-%m-%dT%H:%M format) to
    an equivalent DateTime object. If object is already a
    DateTime object, nothing is changed.
    """
    if type(dt) is datetime.datetime:
        return dt
    return datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M")


# end str_to_datetime

def to_utc(dt):
    """ Converts the input local datetime to UTC. """
    if type(dt) in [str, unicode]:
        dt = str_to_datetime(dt)
    return Local_TZ.to_utc(dt)


# end to_utc()

def from_utc(dt):
    """ Converts the input UTC datetime to local time. """
    if type(dt) in [str, unicode]:
        dt = str_to_datetime(dt)
    return Local_TZ.from_utc(dt)


# end from_utc()

def tzname(dt=None):
    """ Returns the current timezone name. """
    return Local_TZ.tzname(dt)


# end tzname()

def send_mails(recipients, subject, message):
    '''
    Send emails using mailjet
    Args:
        recipients: List of strings. Email addresses of recipients.
        subject: String. Subject line of each email.
        message: String. Plain text message for each email.

    '''
    import mailjet_rest
    import requests_toolbelt.adapters.appengine
    requests_toolbelt.adapters.appengine.monkeypatch()

    from src import secrets
    client = mailjet_rest.Client(
        auth=(secrets.MAILJET_API_KEY, secrets.MAILJET_API_SECRET))

    for recipient in recipients:
        data = {
            'FromEmail': secrets.MAILJET_SENDER,
            'FromName': 'CONSIDER Admin',
            'Subject': subject,
            'Text-part': message,
            'Html-part': message,
            'Recipients': [{'Email': recipient}]
        }
        result = client.send.create(data=data)
        log("Email sent:" + str(result.json()))


# end send_mails

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

# end class RoundEncoder
