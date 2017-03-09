from google.appengine.ext import ndb

from .LogEntry import LogEntry


class ActivityLog(ndb.Model):
    """
    .. _ActivityLog:

    An object which represents the activity log for a group in the app.
    """
    assignment = ndb.KeyProperty(required=True)
    """ Integer. Refers to the section (assignment) to which this entry pertains. """
    course = ndb.KeyProperty(required=True)
    """ Integer. Refers to the course to which this entry pertains. """

    def create_log(self):
        # add log entry about group/log creation
        new_entry = LogEntry(parent=self.key)
        # add description field
        new_entry.description = "Group created"
        # update datastore entries
        new_entry.put()

    def new_entry(self, description, student=None):
        # create new entry
        new_entry = LogEntry(parent=self.key)
        # if student optional parameter is included, set it
        if student:
            new_entry.student = student
        new_entry.description = description

        # TODO: Handle the link

        new_entry.put()