"""
feedbackviewer.py
~~~~~~~~~~~~~~~~~

- Author(s): Daniel Stelsson
- Last Modified: April 6, 2017

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class ViewFeedBackPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)

            feedback = model.Feedback.query()
            feedback = feedback.order(-model.Feedback.timestamp)
            feedback = feedback.fetch()

            from src import config
            template_values = {
                'documentation': config.DOCUMENTATION,
                'logouturl': logout_url,
                'feedback' : feedback
            }
            # Set the template html page
            template = utils.jinja_env().get_template('view_feedback.html')
            # And render it
            self.response.write(template.render(template_values))
            # end get
        else:
            return self.redirect('/')

    def post(self):
       #get id of feedback obj in question
        id = self.request.get('id')

       #get model obj from id
        fb = model.Feedback.get_by_id(int(id))
        if fb:
       #determine which action to take: advance ticket or delete
            action = self.request.get('action')
            if action == "ADVANCE":
                fb.advance_ticket_status()
            elif action == "OPEN":
                fb.mark_ticket_as("OPEN")
            elif action == "IN PROGRESS":
                fb.mark_ticket_as("IN PROGRESS")
            elif action == "CLOSED":
                fb.mark_ticket_as("CLOSED")
            elif action ==  "ARCHIVE":
                fb.is_archived = True
            elif action == "DELETE":
                fb.key.delete()
            elif action == "REACTIVATE":
                fb.is_archived = False
            fb.put()
        else:
            import logging
            logging.info("fb object not found for id: " + id)
