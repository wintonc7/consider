"""
groups.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Grader control over group formation within the app.

- Author(s): Capstone team AU16

Refer to comments within /src/controller/grader/init.py for a better
understanding of the code for graders.

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import model, utils


class Groups(webapp2.RequestHandler):
    """
    API to retrieve and display the information of groups formed for the selected course and section.

    """

    def modify_group_count(self, section, group_count):
        """
        Modifies the total number of groups in this section.

        Args:
            section (object):
                Section whose group count is to be modified
            group_count (int):
                The new total number of groups.

        """
        # Double check that the passed in number of groups isn't null
        if not group_count:
            # Error if so
            utils.error('Groups count not available.', handler=self)
        else:
            if section.groups != group_count and group_count > 0:
                # If the total number of groups are not as requested change them
                section.groups = group_count
                section.put()
            # end
            utils.log('Groups modified.', type='Success!', handler=self)
            # end

    # end modify_group_count

    def update_groups(self, section, groups):
        """
        Updates the groups assignments for the given section.

        Args:
            section (object):
                Section whose group assignments are to be updated.
            groups (dict):
                Dictionary of type ``{email:n}``, where ``email`` is the identifier for a student
                and ``n`` is the group-id that student is to be assigned to.

        """
        # Double check that the passed in groups is non-null
        # for keys, values in groups.items():
        #   print(keys)
        #   print(values)
        #   print("--------------")
        if not groups:
            # Error if so
            utils.error('Groups information not available.', handler=self)
        else:
            # Loop over the students in the passed in section
            for student in section.students:
                # Check if the current student's email is in the groups
                if student.email in groups:
                    # Set the student's group number to the index of the group
                    student.group = int(groups[student.email])
                    # And then grab that group model from the database
                    group = model.Group.get_by_id(student.group, parent=section.key)

                    # -------------------Fix group allocation bug
                    group_id = 1
                    while (group_id <= section.groups):
                        pre_group = model.Group.get_by_id(group_id, parent=section.key)
                        if not pre_group:
                            group_id += 1
                            continue
                        if student.email in pre_group.members:
                            break
                        group_id += 1
                    if group_id <= section.groups and group_id != student.group:
                        pre_group.members.remove(student.email)
                        pre_group.size = len(pre_group.members)
                        pre_group.put()
                    # -------------------Fix group allocation bug

                    # Double check that it actually exists
                    if not group:
                        # And create it if not, giving it the proper number
                        group = model.Group(parent=section.key, id=student.group)
                        group.number = student.group
                    # end
                    # Now check if the student is listed in the correct group
                    if student.email not in group.members:
                        # If not, add that student in to the group
                        group.members.append(student.email)
                        # Update the size
                        group.size = len(group.members)
                        # Set the student's alias for that group
                        student.alias = 'S' + str(group.size)
                        # And commit the changes to the group
                        group.put()
                        # end
                        # end
            # end
            # Commit the changes to the section and log it
            section.put()
            utils.log('Groups updated.', handler=self)
            # end

    # end update_groups

    def get(self):
        """
        HTTP GET Method to render the ``/groups`` page for the logged in Grader.

        """
        # First, check that the logged in user is an grader
        grader = utils.check_privilege(model.Role.grader)
        if not grader:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And get the course and section names from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # Grab all the courses and sections for the logged in grader
        template_values = utils.get_template_all_courses_and_sections(grader,
                                                                      course_name.upper(),
                                                                      selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # Check that the current section has at least one round
            if current_section.rounds > 0:

                # Grab the responses from the initial question
                response = model.Response.query(
                    ancestor=model.Round.get_by_id(1, parent=current_section.key).key).fetch()

                no_answer_students = []
                # And loop over the students in this section
                for stu in current_section.students:
                    flag = True
                    # Loop over the responses
                    for res in response:
                        # And check when the response matches the student
                        if res.student == stu.email:
                            # And set the group of the response to the
                            # group of the student who made that response
                            res.group = stu.group
                            flag = False
                            # end
                    # end
                    if flag:
                        no_answer_students.append(stu)
                # end
                # Add the responses and current group to the template values
                template_values['no_answer_students'] = no_answer_students
                template_values['responses'] = response
                template_values['group'] = current_section.groups
                # end
        # end
        # Set the template and render the page
        template_values['logouturl'] = logout_url
        from src import config
        template_values['documentation'] = config.DOCUMENTATION
        template = utils.jinja_env().get_template('grader/groups.html')
        self.response.write(template.render(template_values))

    # end get

    def post(self):
        """
        HTTP POST method to create groups.
        """
        # First, check that the logged in user is an grader
        grader = utils.check_privilege(model.Role.grader)
        if not grader:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, grader)
        # Grab the action from the page
        action = self.request.get('action')
        # Check that the action was actually supplied
        if not action:
            # Error if not
            utils.error('Invalid argument: action is null', handler=self)
        else:
            # Switch on the action
            utils.log('action = ' + action)
            if action == 'add':
                # If add, grab the number of groups from the page
                group_count = int(self.request.get('groups'))
                # And modify the database
                self.modify_group_count(section, group_count)
            elif action == 'update':
                # For update, grab the group settings from the page
                groups = json.loads(self.request.get('groups'))
                # And modify the database
                self.update_groups(section, groups)
            else:
                # Send an error if a different action is supplied
                utils.error('Unknown action' + action if action else 'None', handler=self)
                # end post

# end class Groups
