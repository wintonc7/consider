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
        student = utils.check_privilege(model.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/')
        # end

        feedback = model.Feedback()
        email = self.request.get('email')
        tag = self.request.get('tag')
        othertag = self.request.get('othertag')
        comments = self.request.get('comments')

        if email:
            feedback.email = email
        else:
            feedback.email = "invalid email"
        if tag:
            if tag == "other":
                feedback.other_selected = True
                if othertag:
                    feedback.tag = othertag
                else:
                    feedback.tag = tag
            else:
                feedback.tag = tag
                feedback.other_selected = False
        else:
            feedback.tag = "NO TAG"
        if comments:
            feedback.feedback = comments
        else:
            feedback.feedback = "NO COMMENTS"
        feedback.put()

        return self.redirect('/student_home')
        # end post

    def get(self):
        """
        Displays form for submitting feedback
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/')
        # end

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'student': True,
            'email': student.preferred_email
        }
        # Set the template html page
        template = utils.jinja_env().get_template('students/feedback_form.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
