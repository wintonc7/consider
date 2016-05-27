from google.appengine.ext import ndb


class Question(ndb.Model):
    """
    .. _Question:

    An object to represent the Question in the data store. Currently only multiple choice questions are supported.
    """
    options_total = ndb.IntegerProperty(required=True, indexed=False)
    """ Integer. Number of options for the question. """
    question = ndb.StringProperty(required=True, indexed=False)
    """ String. The text of the question. """
    options = ndb.StringProperty(repeated=True, indexed=False)
    """ List of Strings. Options for this question."""
    # TODO Templates for questions - MCQ, long answers, short answers, etc.


class Round(ndb.Model):  # FIXME move under a Group?
    """
    .. _Round:

    An object to represent the Round in the datastore.

    Child of `Section`_.
    """
    deadline = ndb.StringProperty(required=True, indexed=False)
    """ String. Represents the deadline in the format %Y-%m-%dT%H:%M """
    number = ndb.IntegerProperty(required=True)
    """ Integer. Index of the round."""
    description = ndb.StringProperty(indexed=False)
    """ String. Description or brief instructions for the round."""
    is_quiz = ndb.BooleanProperty(default=False, indexed=False)
    """ Boolean. If ``True``, this is a quiz round (e.g., lead-in question); if ``False``, a discussion round."""
    quiz = ndb.StructuredProperty(Question, indexed=False)
    """ A `Question`_ property. Contains the question if this is a quiz round."""

    # NEW ATTRIBUTES FOR DYNAMIC ROUNDS: PART 1
    starttime = ndb.StringProperty(required=True, indexed=False)
    """ String. Represents the start of the round in the format %Y-%m-%dT%H:%M """
    buffer_time = ndb.IntegerProperty(default=0, indexed=False)
    """ Integer. Represents the buffer time between rounds."""
