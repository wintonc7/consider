from google.appengine.ext import ndb


class Group(ndb.Model):
    """
    .. _Group:

    An object to represent the Group of students in a course section.

    Child of `Section`_.
    """
    number = ndb.IntegerProperty(required=True)
    """ Integer. Index of the group within that `Section`_ """
    members = ndb.StringProperty(repeated=True)
    """ List of Strings. Emails of the `Student`_\ s in this group. """
    size = ndb.IntegerProperty(default=0, indexed=False)
    """ Integer. Size of this group. """
    num_seq_responses = ndb.IntegerProperty(default=0, indexed=False)
