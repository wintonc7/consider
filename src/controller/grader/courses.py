"""
courses.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Grader Courses views.

- Author(s): Capstone team AU16

Refer to comments within /src/controller/grader/init.py for a better
understanding of the code for graders.

--------------------


"""

import webapp2
from google.appengine.api import users

from src import model, utils


class Courses(webapp2.RequestHandler):
    """
    Handles requests for managing courses: adding a course, toggling its status, etc.
    """

    def add_course(self, grader, course_name):
        """
        Adds a course to the datastore.

        Args:
            grader (object):
                Grader who is adding the course.
            course_name (str):
                Name of the course; must be unique across the app.

        """
        # Start by trying to grab the course from the database
        course = model.Course.get_by_id(course_name, parent=grader.key)
        # Check to see if it already exists
        if course:
            # And error if so
            utils.error(course_name + ' already exists', handler=self)
        else:
            # Otherwise, create it, store it in the database, and log it
            course = model.Course(parent=grader.key, id=course_name)
            course.name = course_name
            course.recent_section = ""
            course.put()
            utils.log(course_name + ' added', type='Success!', handler=self)

    # end add_course

    def toggle_course(self, grader, course_name):
        """
        Toggles the status of a course between Active and Inactive.

        Args:
            grader (object):
                Grader whose course is to be toggled.
            course_name (str):
                Name of the course to be toggled.

        """
        # First, grab the course from the database
        course = model.Course.get_by_id(course_name, parent=grader.key)
        if course:
            course.is_active = not course.is_active
            course.put()
            utils.log('Status changed for ' + course_name, type='Success!', handler=self)
        else:
            utils.error('Course ' + course_name + ' not found', handler=self)
            # end

    # end toggle_course

    def post(self):
        """
        HTTP POST method for handling course requests.
        """
        # First, check that the logged in user is an grader
        grader = utils.check_privilege(model.Role.grader)
        if not grader:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, get the course name and action from the webpage
        course_name = self.request.get('name')
        action = self.request.get('action')
        # Double check that they were actually supplied
        if not course_name or not action:
            # Error if not
            utils.error('Invalid argument: course_name or action is null', handler=self)
        else:
            # Now switch based on the action
            if action == 'add':
                # Add course if add
                self.add_course(grader, course_name.upper())
            elif action == 'toggle':
                # Or toggle if toggle
                self.toggle_course(grader, course_name.upper())
            else:
                # If any other action, log it as an error
                utils.error('Unexpected action: ' + action, handler=self)
                # end
                # end

    # end post

    def get(self):
        """
        Display the Course list for this Grader.
        """
        # First, check that the logged in user is an grader
        grader = utils.check_privilege(model.Role.grader)
        if not grader:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, generate a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Log that the current grader is logged in
        utils.log('Grader logged in ' + str(grader))
        # And start building the template values
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'expand': self.request.get('course')
        }
        # Grab the list of courses attributed to the logged in grader
        courses = model.Course.query(ancestor=grader.key).fetch()
        # Double check that they actually have courses
        if courses:
            # Then loop over them
            for course in courses:
                # And grab all the sections attributed to that course
                course.sections = model.Section.query(ancestor=course.key).fetch()
            # end
            # Add all the grader's courses to the template values
            template_values['courses'] = courses
        # end
        # And set the template and render the page
        template = utils.jinja_env().get_template('grader/courses.html')
        self.response.write(template.render(template_values))
        # end get

# end class Courses