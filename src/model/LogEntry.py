from google.appengine.ext import ndb

from . import Student, Section, Course


class LogEntry(ndb.Model):
    """
    .. _LogEntry:

    An object which represents an entry for a log within the app.
    """
    student = ndb.StringProperty(required=True)
    """ String. Student's ID (gmail address). Required. """
    time = ndb.DateTimeProperty(auto_now_add=True)
    """ DateTime. The time when the log entry was created. Automatic. """
    description = ndb.StringProperty()
    """ String. Describes the activity. """
    assignment = ndb.StructuredProperty(Section, required=True)
    """ Section. Refers to the section (assignment) to which this entry pertains. """
    course = ndb.StructuredProperty(Course, required=True)
    """ Course. Refers to the course to which this entry pertains. """
    link = ndb.StringProperty()
    """ String. Link to the part of the site where this entry is relevant. """
