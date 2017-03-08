from google.appengine.ext import ndb

from . import Group, Section, Course, LogEntry


class Log(ndb.Model):
    """
    .. _Log:

    An object which represents the activity log for a group in the app.
    """
    group = ndb.StructuredProperty(Group, required=True)
    """ Group. May be null if this log applies to a Student. Must be non-empty otherwise. """
    assignment = ndb.StructuredProperty(Section, required=True)
    """ Section. Refers to the section (assignment) to which this entry pertains. """
    course = ndb.StructuredProperty(Course, required=True)
    """ Course. Refers to the course to which this entry pertains. """
    log_entries = ndb.StructuredProperty(LogEntry, repeated=True)

    def create_log(self, group_key, assignment, course):
        # create new log
        new_log = Log(parent=group_key)
        # add log entry about group/log creation
        new_entry = LogEntry(parent=new_log.key, assignment=assignment, course=course)
        # add description field
        new_entry.description = "Group created"
        # update datastore entries
        new_entry.put()
        new_log.put()

    def new_entry(self, ):
