"""
admin.py
~~~~~~~~~~~~~~~~~
APIs for handling admin specific tasks of the app, like adding an instructor.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 24, 2015

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

    def add_instructor(self, email):
        """
        Adds an instructor to the datastore.

        Args:
            email: Email of the instructor to be added.
        """
        if email:
            instructor = models.Instructor(id=email)
            instructor.email = email
            instructor.put()
            self.response.write(email + " has been added as an Instructor")
        else:
            self.response.write("Error! invalid arguments.")

    def toggle_instructor(self, email):
        """
        Toggles the status of the selected instructor between 'Active' and 'Inactive'.

        Args:
            email: Email (identifier) of the instructor to be added.

        """
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

    def get(self):
        """
        HTTP GET method to retrieve the list of instructors currently added to the app.
        """
        user = users.get_current_user()

        if user:
            logouturl = users.create_logout_url(self.request.uri)
            template_values = {
                'logouturl': logouturl
            }
            instructors = models.Instructor.query().fetch()
            if instructors:
                template_values['instructors'] = instructors
            template = utils.jinja_env().get_template('admin.html')
            self.response.write(template.render(template_values))
        else:
            loginurl = users.create_login_url(self.request.uri)
            template_values = {
                'loginurl': loginurl
            }
            template = utils.jinja_env().get_template('login.html')
            self.response.write(template.render(template_values))

    def post(self):
        """
        HTTP POST method to add an instructor or toggle the instructor's status.
        Calls appropriate function based on the arguments received.
        """
        email = self.request.get('email').lower()
        action = self.request.get('action')

        if action == 'add':
            self.add_instructor(email)
        else:
            self.toggle_instructor(email)
