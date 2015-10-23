from google.appengine.ext import ndb


class Course(ndb.Model):
    """A model for holding different sections inside a particular Instructor"""
    name = ndb.StringProperty(required=True)
    is_active = ndb.BooleanProperty(default=True, indexed=False)


class Section(ndb.Model):
    """A main model for a particular section which will be child of course"""
    name = ndb.StringProperty(required=True)
    groups = ndb.IntegerProperty(default=0, indexed=False)
    current_round = ndb.IntegerProperty(default=0, indexed=False)
    rounds = ndb.IntegerProperty(default=0, indexed=False)
    students = ndb.StringProperty(repeated=True, indexed=False)
    is_active = ndb.BooleanProperty(default=True, indexed=False)


class Instructor(ndb.Model):
    """A main model for representing admins"""
    email = ndb.StringProperty(required=True)
    is_active = ndb.BooleanProperty(default=True, indexed=False)


class Student(ndb.Model):
    """A student model for all the students"""
    email = ndb.StringProperty(required=True)
    alias = ndb.StringProperty(default='NA')
    group = ndb.IntegerProperty(default=0, indexed=False)
    sections = ndb.KeyProperty(kind=Section, repeated=True, indexed=False)


class Group(ndb.Model):
    """A model to hold the properties of groups of each class"""
    number = ndb.IntegerProperty(required=True)
    members = ndb.StringProperty(repeated=True)
    size = ndb.IntegerProperty(default=0, indexed=False)


class Question(ndb.Model):
    """A model to hold the question and options of each round"""
    options_total = ndb.IntegerProperty(required=True, indexed=False)
    question = ndb.StringProperty(required=True, indexed=False)
    options = ndb.StringProperty(repeated=True, indexed=False)


class Round(ndb.Model):
    """A model to hold the properties of each round"""
    deadline = ndb.StringProperty(required=True, indexed=False)
    number = ndb.IntegerProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    is_quiz = ndb.BooleanProperty(default=False, indexed=False)
    quiz = ndb.StructuredProperty(Question, indexed=False)


class Response(ndb.Model):
    """A response model for all the answers"""
    option = ndb.StringProperty(default='NA', indexed=False)
    comment = ndb.StringProperty(required=True, indexed=False)
    response = ndb.StringProperty(repeated=True, indexed=False)
    summary = ndb.StringProperty(indexed=False)
    student = ndb.StringProperty(required=True)
