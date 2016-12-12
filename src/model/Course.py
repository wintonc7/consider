from google.appengine.ext import ndb

from Section import StudentInfo
from Section import GraderInfo

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

    recent_section = ndb.StringProperty(required=False)
    """ String. ID of the most recent section of this course, to copy the students from. """

    students = ndb.StructuredProperty(StudentInfo, repeated=True)
    """ List of `StudentInfo`_ representing all the `Student`_ entities in this section. """

    graders = ndb.StructuredProperty(GraderInfo, repeated=True)

    export_section = ndb.StringProperty(required=False)