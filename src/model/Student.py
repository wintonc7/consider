from google.appengine.ext import ndb

#from . import Section
import Section

class Student(ndb.Model):
    """
    .. _Student:

    An object to represent the Student in the app.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. Retrieved from Google automatically """
    sections = ndb.KeyProperty(kind=Section, repeated=True, indexed=False)
    """ List of active `Section`_ s this student is enrolled in. """
    preferred_email = ndb.StringProperty()
    """ Additional email addresses to notify. Configured through profile page. """
    fname = ndb.StringProperty()
    """ String. Optional. Configured through profile page. """
    lname = ndb.StringProperty()
    """ String. Optional. Configured through profile page. """