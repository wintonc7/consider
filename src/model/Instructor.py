from google.appengine.ext import ndb


class Instructor(ndb.Model):
    """
    .. _Instructor:

    An object to represent the course Instructor in the app. Parent of the `Course`_ class.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. Retrieved from Gmail automatically """
    is_active = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. Indicates if this instructor is active or not. """