from google.appengine.ext import ndb


class SeqResponse(ndb.Model):
    """
    .. _SeqResponse:

    An object to represent the sequential response.
    """
    index = ndb.IntegerProperty(required=True, indexed=True)
    """ Integer. Index of the response. """
    timestamp = ndb.StringProperty(required=True, indexed=True)
    """ String. Timestamp at which the post was made. """
    author = ndb.StringProperty(required=True, indexed=True)  # FIXME: rename to indicate it's an email
    """ String. Email of the `Student`_ who is the author of this post. """
    author_alias = ndb.StringProperty(default='NA', required=False, indexed=False)
    """ String. Alias of the `Student`_ who is the author of this post. """
    text = ndb.StringProperty(required=False, indexed=False)
    """ String. Text of the response. """
