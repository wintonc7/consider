"""
model.py
~~~~~~~~~~~~~~~~~
Implements the data model for the app.

All the entities derive from ``ndb`` class of Google App Engine.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 18, 2015

--------------------


"""
from google.appengine.ext import ndb
import json

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
    is_active = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. Indicates if this section is active or not. """


class Instructor(ndb.Model):
    """
    .. _Instructor:

    An object to represent the course Instructor in the app. Parent of the `Course`_ class.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. Retrieved from Gmail automatically """
    is_active = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. Indicates if this instructor is active or not. """


class Student(ndb.Model):
    """
    .. _Student:

    An object to represent the Student in the app.
    """
    email = ndb.StringProperty(required=True)
    """ String. Must be non-empty and unique. Retrieved from Google automatically """
    sections = ndb.KeyProperty(kind=Section, repeated=True, indexed=False)
    """ List of active `Section`_ s this student is enrolled in. """


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


class Round(ndb.Model):
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
    is_anonymous = ndb.BooleanProperty(default=True, indexed=False)
    """ Boolean. If ``True``, this is an anonymous round; if ``False``, identities will be revealed."""
    is_quiz = ndb.BooleanProperty(default=False, indexed=False)
    """ Boolean. If ``True``, this is a quiz round (e.g., lead-in question); if ``False``, a discussion round."""
    quiz = ndb.StructuredProperty(Question, indexed=False)
    """ A `Question`_ property. Contains the question if this is a quiz round."""

    #NEW ATTRIBUTES FOR DYNAMIC ROUNDS: PART 1
    starttime = ndb.StringProperty(required=True, indexed=False)
    """ String. Represents the start of the round in the format %Y-%m-%dT%H:%M """


class Response(ndb.Model):
    """
    .. _Response:

    An object to represent all types of student responses.

    Child of `Round`_.
    """
    option = ndb.StringProperty(default='NA', indexed=False)
    """ String. Selected option from the multiple choices, if it's a response to a quiz round."""
    comment = ndb.StringProperty(required=True, indexed=False)
    """ String. Comment no a peer's post from the previous round."""
    response = ndb.StringProperty(repeated=True, indexed=False)
    """ List of Strings. Can take values ``support``, ``disagree`` or ``neutral``."""
    summary = ndb.StringProperty(indexed=False)
    """ String. The summary post in the last round."""
    student = ndb.StringProperty(required=True)
    """ String. Email of the `Student`_ who is the author of this response."""


class Role:
    def __init__(self):
        pass

    instructor = 'INSTRUCTOR'
    student = 'STUDENT'
    admin = 'ADMIN'
