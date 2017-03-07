from google.appengine.ext import ndb

from . import Group, LogEntry


class Log(ndb.Model):
    """
    .. _Log:

    An object which represents the activity log for a group in the app.
    """
    group = ndb.StructuredProperty(Group, required=True)
    """ Group. May be null if this log applies to a Student. Must be non-empty otherwise. """
    log_entries = ndb.StructuredProperty(LogEntry, repeated=True)

    def log_created_entry(self, group_key, assignment, course):
        # create new log
        new_log = Log(parent=group_key)
        # add log entry about group/log creation
        new_entry = LogEntry(parent=new_log.key, assignment=assignment, course=course)
        # add description field
        new_entry.description = "Group created"
        new_entry.put()
        new_log.put()
