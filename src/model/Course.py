from google.appengine.ext import ndb


class Course(ndb.Model):
    """
    .. _Course:

    An object to represent course information in the datastore.

    Parent of the `Section`_ object.

    """
    name = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. """

    is_active = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. Indicates if the course is currently active or not. """
