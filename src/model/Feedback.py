from google.appengine.ext import ndb

#tags = {"Profile", "Question Prompts", "Posting Responses", "Viewing Responses", "Other"}

class Feedback(ndb.Model):

    #email of user submitting feedback
    email = ndb.StringProperty(required=True)

    #check if other was selected
    other_selected = ndb.BooleanProperty(required=True)

    #tag selected for this post
    tag = ndb.StringProperty(required=False)

    #Feedback Response
    #TODO stringproperty limits length, could use text property for longer feedback. howmuch do we need?
    feedback = ndb.StringProperty(required=True)