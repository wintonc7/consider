"""
admin.py
~~~~~~~~~~~~~~~~~
APIs for handling admin specific tasks of the app, like adding an instructor.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: May 21, 2016

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class AdminPage(webapp2.RequestHandler):
    """
    API for the main page (``/admin``) for the admin/developer.
    """

    def add_instructor(self, email):
        """
        Adds an instructor to the datastore.

        Args:
            email (str):
                Email of the instructor to be added.

        """
        if email:
            _instructor = model.Instructor(id=email)
            _instructor.email = email
            _instructor.put()
            utils.log(email + ' has been added as an Instructor', type='Success!', handler=self)
        else:
            utils.error('Invalid arguments: email')

    def toggle_instructor(self, email):
        """
        Toggles the status of the selected instructor between 'Active' and 'Inactive'.

        Args:
            email (str):
                Email (identifier) of the instructor to be added.

        """
        if email:
            _instructor = model.Instructor.query(model.Instructor.email == email).get()
            if _instructor:
                _instructor.is_active = not _instructor.is_active
                _instructor.put()
                utils.log('Status changed for ' + email, handler=self)
            else:
                utils.error('Instructor (' + email + ') not found')
        else:
            utils.error('Invalid arguments: email')

    def get(self):
        """
        HTTP GET method to retrieve the list of instructors currently added to the app.
        """
        user = users.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)
            template_values = {
                'logouturl': logout_url
            }
            instructors = model.Instructor.query().fetch()
            if instructors:
                template_values['instructors'] = instructors
            template = utils.jinja_env().get_template('admin.html')
        else:
            login_url = users.create_login_url(self.request.uri)
            template_values = {
                'loginurl': login_url
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
