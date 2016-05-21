"""
responses.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control over student responses within the app.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: May 21, 2016

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class Responses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, tabbed into different rounds.
    """

    def get(self):
        """
        HTTP GET method to retrieve the responses.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(model.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        #end

        # Create logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And grab the course and section name from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And grab all the other courses and sections for this instructor
        template_values = utils.get_template_all_courses_and_sections(
                            instructor, course_name, selected_section_name)
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # And set the round
            template_values['round'] = current_section.rounds
            # Create a new dict for the responses
            resp = {}
            # And loop over the number of rounds (indexed at 1 for lead-in)
            for i in range(1, current_section.rounds + 1):
                response = model.Response.query(
                        ancestor=model.Round.get_by_id(i, parent=current_section.key).key).fetch()
                # response is a list of all the responses for the round i
                if response:
                    resp[str(i)] = response
                #end
            #end
            # Add the responses to the template values
            template_values['responses'] = resp
        #end
        # And set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor/responses.html')
        self.response.write(template.render(template_values))
    #end get

#end class Responses
