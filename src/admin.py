"""
admin.py
~~~~~~~~~~~~~~~~~
APIs for handling admin specific tasks of the app, like adding an instructor.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 18, 2015

--------------------


"""
import logging

import webapp2
from google.appengine.api import users

import models
import utils


class AdminPage(webapp2.RequestHandler):
    """
    API for the main page (``/admin``) for the admin/developer.
    """

    def get(self):
        """
        HTTP GET method to retrieve the list of instructors currently added to the app.
        """
        user = users.get_current_user()

        if user:
            # if users.is_current_user_admin():
            url = users.create_logout_url(self.request.uri)  # TODO default dest. after logout should be /home
            template_values = {
                'url': url
            }
            instructors = models.Instructor.query().fetch()
            if instructors:
                template_values['instructors'] = instructors
            template = utils.jinja_env().get_template('admin.html')
            self.response.write(template.render(template_values))
            # else:
            #     self.response.write("You are not Rohit :p")
        else:
            url = users.create_login_url(self.request.uri)
            template_values = {
                'url': url
            }
            template = utils.jinja_env().get_template('login.html')
            self.response.write(template.render(template_values))

    def post(self):
        """
        HTTP POST method to add an instructor.
        """
        email = self.request.get('email').lower()

        # if users.is_current_user_admin():
        if email:
            instructor = models.Instructor(id=email)
            instructor.email = email
            instructor.put()
            self.response.write(email + " has been added as an Instructor")
        else:
            self.response.write("Error! invalid arguments.")


class AdminToggleInstructor(webapp2.RequestHandler):
    """
    API to activate or deactivate an instructor.
    """

    def post(self):
        """
        HTTP POST method to toggle the instructor's status.
        """
        # if users.is_current_user_admin():
        email = self.request.get('email')
        if email:
            logging.info("Changing status of " + email)
            instructor = models.Instructor.query(models.Instructor.email == email).get()
            if instructor:
                instructor.is_active = not instructor.is_active
                instructor.put()
                self.response.write("Status changed for " + email)
            else:
                self.response.write("Instructor not found in the database.")
        else:
            self.response.write("Error! invalid arguments.")
