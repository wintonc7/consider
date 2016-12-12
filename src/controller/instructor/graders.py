"""
graders.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding/removing graders.

- Author(s): Capstone team AU16

Refer to comments within /src/controller/grader/init.py for a better
understanding of the code for graders.

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import model, utils

class Graders(webapp2.RequestHandler):
    """
    API to add a grader to the given section and course.
    """

    def add_graders(self, section, emails):
        """
        Adds one or more graders to the given section in the datastore.

        Args:
            section (object):
                Section to which the studetns are to be added.
            emails (str):
                Emails (IDs) of graders to be added.

        """
        # Start by looping over the list of emails supplied
        for email in emails:
            # Transform the supplied email to lowercase
            email = email.lower()
            # Then make a list of all the emails currently in the section
            grader_emails = [s.email for s in section.graders]
            # Check that the supplied email isn't already in the section
            if email not in grader_emails:
                # And add them to the list of students for the section
                info = model.GraderInfo()
                utils.log(info)
                info.email = email
                section.graders.append(info)
            # end
            # Now grab the grader from the database
            grader = model.Grader.get_by_id(email)
            # And if they don't already have a db entry
            if not grader:
                # Create a new grader and assign the email address
                grader = model.Grader(id=email)
                grader.email = email
            # end
            # Now check if the current grader is subscribed to this section
            if section.key not in grader.sections:
                # And add them if they weren't already
                grader.sections.append(section.key)
            # end
            # Save the grader data back to the database
            grader.put()
        # end
        # Now save all the section data back to the database and log it
        section.put()
        utils.log('Graders added to Section ' + str(section), type='Success!')

    # end add_graders

    def remove_grader(self, section, email):
        """
        Removes a specific graders from the given section.

        Args:
            section (object):
                Section from which the grader is to be removed.
            email (str):
                Email (ID) of the grader to be removed.

        """
        # First, grab the grader from the db by the email passed in
        grader = model.Grader.get_by_id(email)
        # Check that there is actually a record for that email
        if not grader:
            # And error if not
            utils.error('Grader does not exist!', handler=self)
        else:
            # Create a new list for the section removing the grader
            section.graders = [s for s in section.graders if s.email != email]  # TODO better? use remove?
            # Check if the grader is enrolled in this section
            if section.key in grader.sections:
                # And remove them if so
                grader.sections.remove(section.key)
            # end
            # And save both the grader and section back to the db and log it
            grader.put()
            section.put()
            utils.log(
                'Grader {0} has been removed from Section {1}'.format(str(grader),
                                                                       str(section)), handler=self, type='Success!')
            # end

    # end remove_grader

    def post(self):
        """
        HTTP POST method to add the grader.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(model.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab the action from the page
        action = self.request.get('action')
        # Check that the action was actually supplied
        print(action)
        if not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add':
                # Grab a list of the emails from the page
                emails = json.loads(self.request.get('emails'))
                # And create new graders from that list
                self.add_graders(section, emails)
            elif action == 'remove':
                # Grab the email from the page to remove
                email = self.request.get('email').lower()
                # And remove it
                self.remove_grader(section, email)
            else:
                # Send an error if any other action is supplied
                utils.error('Unexpected action: ' + action, handler=self)
                # end
                # end

    # end post

    def get(self):
        """
        HTTP GET method to retrieve the list of graders from the datastore.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(model.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Get the course and section name from the webpage
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And start building the template values
        template_values = utils.get_template_all_courses_and_sections(instructor, course_name.upper(),
                                                                      selected_section_name.upper())
        template_values['logouturl'] = logout_url
        from src import config
        template_values['documentation'] = config.DOCUMENTATION
        # Set the template and render the page
        template = utils.jinja_env().get_template('instructor/list_graders.html')
        self.response.write(template.render(template_values))
        # end get

#end class Graders