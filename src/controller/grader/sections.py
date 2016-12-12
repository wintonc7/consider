"""
section.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Grader control of adding/removing sections.

- Author(s): Capstone team AU16

Refer to comments within /src/controller/grader/init.py for a better
understanding of the code for graders.

--------------------


"""
import webapp2
import csv
from datetime import datetime

from src import model, utils


class Sections(webapp2.RequestHandler):
    """
    Handles requests for managing sections: adding a section, toggling its status, etc.
    """

    def add_section(self, course, section_name):
        """
        Adds a section to the given course in the datastore.

        Args:
            course (object):
                Course to which the section is to be added.
            section_name (str):
                Name of the section; must be unique within the course.

        """
        # First, start by grabbing the section passed in from the database
        section = model.Section.get_by_id(section_name, parent=course.key)
        # Double check that it doesn't already exist
        if section:
            # And send an error if it does
            utils.error(section_name + ' already exists', handler=self)
        else:
            # Otherwise, create it, save it to the database, and log it
            section = model.Section(parent=course.key, id=section_name)
            section.name = section_name
            section.put()
            utils.log(section_name + ' added', type='Success!')
            # TODO Include `Students from {{recent_section}} added to the {{current_section}}` - when it shows the 'Success' box after adding a section?
            if course.recent_section:
                recent_section = model.Section.get_by_id(course.recent_section, parent=course.key)
                for s in recent_section.students:
                    section.students.append(s)
                    student = model.Student.get_by_id(s.email)
                    if section.key not in student.sections:
                        student.sections.append(section.key)
                        student.put()
                    section.put()

    # end add_section

    def toggle_section(self, course, section_name):
        """
        Toggles the status of a section between Active and Inactive.

        Args:
            course (object):
                Course under which this section exists
            section_name (str):
                Name of the section to be toggled.

        """
        # First, start by grabbing the section from the passed in value
        _section = model.Section.get_by_id(section_name, parent=course.key)
        # Double check that it actually exists
        if _section:
            # Toggle the section to active, save it to the database, and log it
            _section.is_active = not _section.is_active
            _section.put()
            utils.log('Status changed for ' + section_name, type='Success!')
        else:
            # Send an error if the section passed in doesn't exist
            utils.error('Section ' + section_name + ' not found', handler=self)
            # end

    # end toggle_section

    def post(self):
        """
        HTTP POST method to add a section to a course.
        """
        # First, check that the logged in user is an grader
        grader = utils.check_privilege(model.Role.grader)
        if not grader:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, grab the course, section, and action from the webpage
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        action = self.request.get('action')
        # Double check that all three were supplied
        if not course_name or not section_name or not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            # Otherwise, grab the course from the database
            course = model.Course.get_by_id(course_name.upper(), parent=grader.key)
            # And check that it exists and is active
            if not course or not course.is_active:
                # Error if not
                utils.error(course_name + ' does not exist OR is not active!', handler=self)
            else:
                # Otherwise, switch on the action
                if action == 'add':
                    # Add a new section if action is add
                    self.add_section(course, section_name.upper())
                elif action == 'toggle':
                    # Or toggle
                    self.toggle_section(course, section_name.upper())
                else:
                    # Error if the action is neither toggle or add
                    utils.error('Unexpected action:' + action, handler=self)

    # end post

    def get(self):
        self.redirect('/courses')

        # end get

# end class Section
