from google.appengine.ext import ndb

from . import Section

""" 
- Author(s): Capstone team AU16

Refer to comments within /src/controller/grader/init.py for a better
understanding of the code for graders.

"""

class Grader(ndb.Model):
    """
    .. _Grader:

    An object to represent the course Grader in the app. Parent of the `Course`_ class.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. Retrieved from Gmail automatically """
    is_active = ndb.BooleanProperty(default=True, indexed=False)