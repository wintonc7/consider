"""
activitylog.py
~~~~~~~~~~~~~~~~~
Implements the APIs for the Student activity log in the app.

- Author(s): Alan Zeigler
- Last Modified: March 5, 2017

--------------------


"""

import webapp2, json, StringIO
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
            student_groups = [group for group in groups if student.email in group.members]
        logs = []
        for group in student_groups:
            logs.extend(model.ActivityLog.query(ancestor=group.key).fetch())
        log_entries = []
        for log in logs:
            log_entries.extend(model.LogEntry.query(ancestor=log.key).fetch())
            new_dict = {
                "course": log.course.get().name,
                "assignment": log.assignment.get().name,
                "entries": []
            }
            output['courses'].append(log.course.get().name)
            output['assignments'].append(log.assignment.get().name)
            for log_entry in log_entries:
                new_dict['entries'].append({
                    "student": log_entry.student,
                    "description": log_entry.description,
                    "time": log_entry.time.strftime("%c")
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
