from google.appengine.ext import ndb


class LogEntry(ndb.Model):
    """
    .. _LogEntry:

    An object which represents an entry for a log within the app.
    """
    student = ndb.StringProperty()
    """ String. Student's ID (gmail address). """
    time = ndb.DateTimeProperty(auto_now_add=True)
    """ DateTime. The time when the log entry was created. Automatic. """
    description = ndb.StringProperty()
    """ String. Describes the activity. """
    link = ndb.StringProperty()
    """ String. Link to the part of the site where this entry is relevant. """
