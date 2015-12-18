import logging

import webapp2
from google.appengine.api import users

import consider
from model import Instructor


class AdminPage(webapp2.RequestHandler):
    """Main function that will handle the first request"""

    def get(self):
        user = users.get_current_user()

        if user:
            # if users.is_current_user_admin():
            url = users.create_logout_url(self.request.uri)
            template_values = {
                'url': url
            }
            instructors = Instructor.query().fetch()
            if instructors:
                template_values['instructors'] = instructors
            template = consider.JINJA_ENVIRONMENT.get_template('developer.html')
            self.response.write(template.render(template_values))
            # else:
            #     self.response.write("You are not Rohit :p")
        else:
            url = users.create_login_url(self.request.uri)
            template_values = {
                'url': url
            }
            template = consider.JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))

    def post(self):
        email = self.request.get('email').lower()

        # if users.is_current_user_admin():
        if email:
            instructor = Instructor(id=email)
            instructor.email = email
            instructor.put()
            self.response.write(email + " has been added as an Instructor")
        else:
            self.response.write("Error! invalid arguments.")


class AdminToggleInstructor(webapp2.RequestHandler):
    """Changing status of Instructor in the database"""

    def post(self):
        # if users.is_current_user_admin():
        email = self.request.get('email')
        if email:
            logging.info("Changing status of " + email)
            instructor = Instructor.query(Instructor.email == email).get()
            if instructor:
                instructor.is_active = not instructor.is_active
                instructor.put()
                self.response.write("Status changed for " + email)
            else:
                self.response.write("Instructor not found in the database.")
        else:
            self.response.write("Error! invalid arguments.")
