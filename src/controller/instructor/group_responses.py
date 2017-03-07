"""
group_responses.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: May 30, 2016

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class GroupResponses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, organized into groups.
    """

    def get(self):
        """
        HTTP GET method to retrieve the group responses.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(model.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # TODO: Display seq. responses, like in response.py

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And get the course and section name from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And grab the other courses and sections from this instructor
        template_values = utils.get_template_all_courses_and_sections(
            instructor, course_name, selected_section_name)
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab the current section from the template values
            current_section = template_values['selectedSectionObject']
            # Set the rounds and groups
            template_values['round'] = current_section.rounds
            template_values['groups'] = current_section.groups

            # And check that groups have actually been assigned
            if current_section.groups > 0:
                # Create a new dict for responses
                resp = {}
                # Loop over the groups (indexed by 1)
                for g in range(1, current_section.groups + 1):
                    # And loop over the rounds (indexed by 1)
                    for r in range(1, current_section.rounds + 1):
                        # Now set an empty list for each group and round
                        resp['group_' + str(g) + '_' + str(r)] = []
                        # end
                # end
                # Loop over the number of rounds (indexed by 1)
                for r in range(1, current_section.rounds + 1):
                    # Grab the responses for that round from the db
                    responses = model.Response.query(
                        ancestor=model.Round.get_by_id(r, parent=current_section.key).key).fetch()
                    # Double check that the responses actually exist
                    if responses:
                        # And loop over the responses
                        for res in responses:
                            # And loop over the students in this section
                            for s in current_section.students:
                                # Check that the email of the student
                                # and the email of the response match
                                # and that the student is in a group
                                if s.email == res.student and s.group != 0:
                                    # Set the alias of the response
                                    res.alias = s.alias
                                    # Append the response to the appropriate
                                    # group and round
                                    resp['group_' + str(s.group) + '_' + str(r)].append(res)
                                    break
                                    # end
                                    # end
                                    # end
                                    # end
                # end
                # And set the template values for all the responses
                template_values['responses'] = resp
                # end
        # end
        # And set the template and render the page
        template_values['logouturl'] = logout_url
        from src import config
        template_values['documentation'] = config.DOCUMENTATION
        template = utils.jinja_env().get_template('instructor/groups_responses.html')
        self.response.write(template.render(template_values))
        # end get

# end class GroupResponses
