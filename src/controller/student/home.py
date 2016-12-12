"""
home.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Student homepage in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: May 27, 2016

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class HomePage(webapp2.RequestHandler):
    def get(self):
        """
        Display a list of active ``Section``_\ s this ``Student``_ is enrolled in.
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/')
        # end

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        students = [student]
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'nickname': student.email
        }
        # Grab the sections the student is a part of
        sections = student.sections
        # Create a new list for holding the section objects from the db
        section_list = []
        # Double check that the student is actually enrolled in a section
        if sections:
            # Loop over all the sections they're in
            for section in sections:
                # Grab it from the db
                section_obj = section.get()
                if section_obj.is_active:
                    # Get the parent course for the section
                    course_obj = section.parent().get()
                    # Double check that both exist
                    if section_obj and course_obj:
                        # Grab the section key, section name, and course name
                        sec = {
                            'key': section.urlsafe(),
                            'name': section_obj.name,
                            'course': course_obj.name,
                            'group': findGroupIDByEmail(section_obj, student.email),
                            'round': utils.get_current_round(section_obj)
                        }
                        # And throw it in the list
                        section_list.append(sec)
                        # end
                        # end
        # end
        # Add the list of sections the student is in to our template
        template_values['sections'] = section_list
        # Set the template html page
        template = utils.jinja_env().get_template('students/home.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get



# end class HomePage

def findGroupIDByEmail(section, email):
    for student in section.students:
        if student.email == email:
            return student.group
