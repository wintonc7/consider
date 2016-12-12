"""
students.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding/removing students.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: May 30, 2016

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import model, utils


class Students(webapp2.RequestHandler):
    """
    API to add a student to the given section and course.
    """

    def add_students(self, section, emails):
        """
        Adds one or more students to the given section in the datastore.

        Args:
            section (object):
                Section to which the studetns are to be added.
            emails (list):
                Emails (IDs) of students to be added.

        """
        # Start by looping over the list of emails supplied
        for email in emails:
            # Transform the supplied email to lowercase
            email = email.lower()
            # Then make a list of all the emails currently in the section
            student_emails = [s.email for s in section.students]
            # Check that the supplied email isn't already in the section
            if email not in student_emails:
                # And add them to the list of students for the section
                info = model.StudentInfo()
                info.email = email
                section.students.append(info)
            # end
            # Now grab the student from the database
            student = model.Student.get_by_id(email)
            # And if they don't already have a db entry
            if not student:
                # Create a new student and assign the email address
                student = model.Student(id=email)
                student.email = email
            # end
            # Now check if the current student is subscribed to this section
            if section.key not in student.sections:
                # And add them if they weren't already
                student.sections.append(section.key)
            # end
            # Save the student data back to the database
            student.put()
        # end
        # Now save all the section data back to the database and log it
        section.put()
        utils.log('Students added to Section ' + str(section), type='Success!')

    # end add_students

    def remove_student(self, section, email):
        """
        Removes a specific students from the given section.

        Args:
            section (object):
                Section from which the student is to be removed.
            email (str):
                Email (ID) of the student to be removed.

        """
        # First, grab the student from the db by the email passed in
        student = model.Student.get_by_id(email)
        # Check that there is actually a record for that email
        if not student:
            # And error if not
            utils.error('Student does not exist!', handler=self)
        else:
            # Create a new list for the section removing the student
            section.students = [s for s in section.students if s.email != email]  # TODO better? use remove?
            # Check if the student is enrolled in this section
            if section.key in student.sections:
                # And remove them if so
                student.sections.remove(section.key)
            # end
            # And save both the student and section back to the db and log it
            student.put()
            section.put()
            utils.log(
                'Student {0} has been removed from Section {1}'.format(str(student),
                                                                       str(section)), handler=self, type='Success!')
            # end

    # end remove_student

    def post(self):
        """
        HTTP POST method to add the student.
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
        if not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or actoin is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add':
                # Grab a list of the emails from the page
                emails = json.loads(self.request.get('emails'))
                # And create new students from that list
                self.add_students(section, emails)
            elif action == 'remove':
                # Grab the email from the page to remove
                email = self.request.get('email').lower()
                # And remove it
                self.remove_student(section, email)
            else:
                # Send an error if any other action is supplied
                utils.error('Unexpected action: ' + action, handler=self)
                # end
                # end

    # end post

    def get(self):
        """
        HTTP GET method to retrieve the list of students from the datastore.
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
        template = utils.jinja_env().get_template('instructor/list_students.html')
        self.response.write(template.render(template_values))
        # end get

# end class Students
