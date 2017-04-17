"""
feedbackform.py
~~~~~~~~~~~~~~~~~
Implements the APIs for the Student activity log in the app.

- Author(s): Daniel Stelson
- Last Modified: April 2, 2017

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class FeedbackForm(webapp2.RequestHandler):
    def post(self):
        """
        HTTP POST method to submit the response.
        """
        # First, check that the logged in user is a student
        is_student = True;
        user = utils.check_privilege(model.Role.student)
        if not user:
            # Redirect home if not a student
            user = utils.check_privilege(model.Role.instructor)
            is_student = False
            if not user:
                return self.redirect("/")
        # end

        feedback = model.Feedback()
        email = self.request.get('email')
        tags = self.request.get('tags')
        othertag = self.request.get('othertag')
        comments = self.request.get('comments')

        if email == "false":
            if is_student:
                feedback.email = user.preferred_email
            else:
                feedback.email = user.email
        else:
            feedback.email = "ANONYMOUS"
        if tags:
            tags = tags[:-1]
            split_tags = tags.split(",")
            feedback.tags = split_tags
        else:
            feedback.tag = "NO TAGS"
        if comments:
            feedback.feedback = comments
        else:
            feedback.feedback = "NO COMMENTS"
        feedback.other_selected = (othertag == "true")
        feedback.ticket_status = "OPEN"
        feedback.is_archived = False;

        feedback.put()
        if(is_student):
            return self.redirect('/student_home')
        else:
            return self.redirect('/courses')
        # end post

    def get(self):
        """
        Displays form for submitting feedback
        """
        # First, check that the logged in user is a student
        is_student = True;
        user = utils.check_privilege(model.Role.student)
        if not user:
            # Redirect home if not a student
            user = utils.check_privilege(model.Role.instructor)
            is_student = False
            if not user:
                return self.redirect("/")
        # end

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'is_student': is_student,
        }
        if is_student:
            template_values['email'] = user.preferred_email
        else:
            template_values['email'] = user.email
        # Set the template html page
        template = utils.jinja_env().get_template('feedback_form.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
