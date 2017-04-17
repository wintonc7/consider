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

    #status of feedback ticket
    #Status flow Open -> In Progress -> Closed
    ticket_status = ndb.StringProperty(required=True)

    #indicator if ticket is archived
    is_archived = ndb.BooleanProperty(required=True)

    def advance_ticket_status(self):
        if self.ticket_status == "OPEN":
            self.ticket_status = "IN PROGRESS"
        elif self.ticket_status == "IN PROGRESS":
            self.ticket_status = "CLOSED"
        elif self.ticket_status == "CLOSED":
            self.ticket_status = "CLOSED"
        else:
            self.ticket_status = "OPEN"
        self.put()

    def mark_ticket_as(self, status):
        self.ticket_status=status
        self.put()

