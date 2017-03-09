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
        output = {"logs": []}
        groups = []
        for section_key in student.sections:
            groups.extend(model.Group.query(ancestor=section_key).fetch())
        logs = []
        for group in groups:
            logs.extend(model.ActivityLog.query(ancestor=group.key).fetch())
        log_entries = []
        for log in logs:
            log_entries.extend(model.LogEntry.query(ancestor=log.key).fetch())
            new_dict = {
                "course": log.course.get().name,
                "assignment": log.assignment.get().name,
                "entries": []
            }
            for log_entry in log_entries:
                new_dict['entries'].append({
                    "student": log_entry.student,
                    "description": log_entry.description,
                    "time": log_entry.time.strftime("%c")
                })
            output['logs'].append(new_dict)

        # Format log entries as JSON and export
        output_string = json.dumps(output)
        self.response.headers.add_header("Logs", output_string)

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        # Set up the template
        from src import config
        template_values = {
            'documentation': config.DOCUMENTATION,
            'logouturl': logout_url,
            'student': True
        }
        # Set the template html page
        template = utils.jinja_env().get_template('students/activitylog.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get
