from google.appengine.ext import ndb


class Response(ndb.Model):
    """
    .. _Response:

    An object to represent all types of student responses.

    Child of `Round`_.
    """
    option = ndb.StringProperty(default='NA', indexed=False)
    """ String. Selected option from the multiple choices, if it's a response to a quiz round."""
    comment = ndb.StringProperty(required=True, indexed=False)
    """ String. Comment on a peer's post from the previous round."""
    response = ndb.StringProperty(repeated=True, indexed=False)
    """ List of Strings. Can take values ``support``, ``disagree`` or ``neutral``."""
    summary = ndb.StringProperty(indexed=False)
    """ String. The summary post in the last round."""
    student = ndb.StringProperty(required=True)
    """ String. Email of the `Student`_ who is the author of this response."""
