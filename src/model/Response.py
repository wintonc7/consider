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
    student = ndb.StringProperty(required=True, indexed=True)
    """ String. Email of the `Student`_ who is the author of this response."""
    thumbs = ndb.JsonProperty(default={})
    """ JSON. Indicates how others responded to this post in the followup round. """

    def add_to_thumbs(self, in_key, in_value):
        if not self.thumbs:
            self.thumbs = {}
        self.thumbs[in_key] = in_value

    def get_response_by_student(round_key, student_email):
        req_response = Response.query(ancestor=round_key).filter(Response.student == student_email).fetch(1)
        return req_response if req_response else None
