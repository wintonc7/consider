"""
activitylog.py
~~~~~~~~~~~~~~~~~
Implements the APIs for the Student activity log in the app.

- Author(s): Alan Zeigler
- Last Modified: March 5, 2017

--------------------


"""

import webapp2, logging
from google.appengine.api import users

from src import model, utils


class ActivityLog(webapp2.RequestHandler):
    def get(self):
        """
        Obtains all relevant log entries for the logged in student
        """

        # First, check that logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            #Redirect home if not a student
            return self.redirect('/')
        # end

        # Use obtained user object to obtain relevant log entries
        output = {"logs": [], "courses": [], "assignments": []}
        student_groups = []
        for section_key in student.sections:
            groups = model.Group.query(ancestor=section_key).fetch()
            student_groups.extend([group for group in groups if student.email in group.members])
        logs = []
        for group in student_groups:
            logs.extend(model.ActivityLog.query(ancestor=group.key).fetch())
        for log in logs:
            log_entries = (model.LogEntry.query(ancestor=log.key).fetch())
            course_name = log.course.get().name
            assignment_name = log.assignment.get().name
            if (course_name not in output['courses']):
                output['courses'].append(course_name)
            if (assignment_name not in output['assignments']):
                output['assignments'].append(assignment_name)
            new_dict = {
                "course": course_name,
                "assignment": assignment_name,
                "link": "",
                "entries": []
            }
            for log_entry in log_entries:
                new_dict['entries'].append({
                    "student": log_entry.student,
                    "description": log_entry.description,
                    "time": log_entry.time.strftime("%c"),
                    "link": log_entry.link
                })
            output['logs'].append(new_dict)

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'student': True,
            'courses': output['courses'],
            'assignments': output['assignments'],
            'logs': output['logs']
        }
        # Set the template html page
        template = utils.jinja_env().get_template('students/activitylog.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
