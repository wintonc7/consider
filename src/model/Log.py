from google.appengine.ext import ndb

from . import Group, LogEntry


class Log(ndb.Model):
    """
    .. _Log:

    An object which represents the activity log for a group in the app.
    """
    group = ndb.StructuredProperty(Group)
    """ Group. May be null if this log applies to a Student. Must be non-empty otherwise. """
    log_entries = ndb.StructuredProperty(LogEntry, repeated=True)
