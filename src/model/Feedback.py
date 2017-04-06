from google.appengine.ext import ndb

#tags = {"Profile", "Question Prompts", "Posting Responses", "Viewing Responses", "Other"}

class Feedback(ndb.Model):

    #email of user submitting feedback
    email = ndb.StringProperty(required=True)

    #check if other was selected
    other_selected = ndb.BooleanProperty(required=True)

    #tag(s) selected for this post
    tags = ndb.StringProperty(required=False, repeated=True)

    #Feedback Response
    feedback = ndb.StringProperty(required=True)

    #Timestamp of feedback submisssion
    timestamp = ndb.DateTimeProperty(auto_now_add=True)