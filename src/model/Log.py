from google.appengine.ext import ndb

from . import Student, Group, LogEntry


class Log(ndb.Model):
    """
    .. _Log:

    An object which represents the activity log for a student or group in the app.
    """
    student = ndb.StructuredProperty(Student)
    """ Student. May be null if this log applies to a Group. Must be non-empty otherwise. """
    group = ndb.StructuredProperty(Group)
    """ Group. May be null if this log applies to a Student. Must be non-empty otherwise. """
    log_entries = ndb.StructuredProperty(LogEntry, repeated=True)
