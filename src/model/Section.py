from google.appengine.ext import ndb


class StudentInfo(ndb.Model):
    """
    .. _StudentInfo:

    An object to represent a student's information in the datastore.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. """
    alias = ndb.StringProperty(default='NA', indexed=False)
    """ String. Identifies a student within a discussion round. Takes values S1, S2, etc. """
    group = ndb.IntegerProperty(default=0)
    """ Integer. The group this student is part of. """

class GraderInfo(ndb.Model):
    """
    .. _GraderInfo:

    An object to represent a grader's information in the datastore.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. """
    alias = ndb.StringProperty(default='NA', indexed=False)
    """ String. Identifies a grader within a discussion round. Takes values S1, S2, etc. """
    group = ndb.IntegerProperty(default=0)
    """ Integer. The group this grader is part of. """

class Section(ndb.Model):
    """
    .. _Section:

    An object to represent section information in the datastore.

    Child of the `Course`_ object. Parent of `Round`_\ , `Group`_\ , `Response`_\ .
    """
    name = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique within a course. """
    groups = ndb.IntegerProperty(default=0, indexed=False)
    """ Integer. Number of groups in this section. (default: 0) """
    current_round = ndb.IntegerProperty(default=0, indexed=False)
    """ Integer. Index of the current round. (default: 0) """
    rounds = ndb.IntegerProperty(default=0, indexed=False)
    """ Integer. Number of rounds for this section. (default: 0)"""
    students = ndb.StructuredProperty(StudentInfo, repeated=True)
    """ List of `StudentInfo`_ representing all the `Student`_ entities in this section. """
    graders = ndb.StructuredProperty(GraderInfo, repeated=True)
    """ new grader code """
    is_active = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. Indicates if this section is active or not. """
    is_anonymous = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. If ``True``, discussions in this `Section`_ are anonymous; if ``False``, identities are revealed."""
    has_rounds = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. If ``True``, asynchronous, rounds-based discussion, else sequential """
    export_info = ndb.StringProperty(required=False) # FIXME What is this and why is it needed? Used in HTML export

    def find_student_info(self, email):
        if self.students:
            return next(s for s in self.students if s.email == email)
        else:
            return None

    def find_grader_info(self, email):
        if self.graders:
            return next(s for s in self.graders if s.email == email)
        else:
            return None

""" New grader code """


