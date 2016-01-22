"""
instructor.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Jan. 13, 2016

--------------------


"""
import json

import webapp2
from google.appengine.api import users

import models
import utils


class Courses(webapp2.RequestHandler):
    """
    Handles requests for managing courses: adding a course, toggling its status, etc.
    """

    def add_course(self, instructor, course_name):
        """
        Adds a course to the datastore.

        Args:
            instructor (object):
                Instructor who is adding the course.
            course_name (str):
                Name of the course; must be unique across the app.

        """
        course = models.Course.get_by_id(course_name, parent=instructor.key)
        if course:
            utils.error(course_name + ' already exists', handler=self)
        else:
            course = models.Course(parent=instructor.key, id=course_name)
            course.name = course_name
            course.put()
            utils.log(course_name + ' added', type='S',handler=self)

    def toggle_course(self, instructor, course_name):
        """
        Toggles the status of a course between Active and Inactive.

        Args:
            instructor (object):
                Instructor whose course is to be toggled.
            course_name (str):
                Name of the course to be toggled.

        """
        course = models.Course.get_by_id(course_name, parent=instructor.key)
        if course:
            course.is_active = not course.is_active
            course.put()
            utils.log('Status changed for ' + course_name, type='S',handler=self)
        else:
            utils.error('Course ' + course_name + ' not found', handler=self)

    def post(self):
        """
        HTTP POST method for handling course requests.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            course_name = self.request.get('name')
            action = self.request.get('action')

            if course_name and action:
                if action == 'add':
                    self.add_course(user, course_name.upper())
                elif action == 'toggle':
                    self.toggle_course(user, course_name.upper())
                else:
                    utils.error('Unexpected action: ' + action,handler=self)
            else:
                utils.error('Invalid argument: course_name or action is null', handler=self)
        else:
            utils.error('user is null or not Instructor', handler=self)

    def get(self):
        """
        Display the Course list for this Instructor.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            utils.log('Instructor logged in ' + str(user))
            template_values = {'logouturl': logout_url, 'expand': self.request.get('course')}
            courses = models.Course.query(ancestor=user.key).fetch()
            if courses:
                for course in courses:
                    course.sections = models.Section.query(ancestor=course.key).fetch()
                template_values['courses'] = courses
            template = utils.jinja_env().get_template('instructor_courses.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user is None or not Instructor', handler=self)
            self.redirect('/')


class Section(webapp2.RequestHandler):
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
        section = models.Section.get_by_id(section_name, parent=course.key)
        if section:
            utils.error(section_name + ' already exists')
        else:
            section = models.Section(parent=course.key, id=section_name)
            section.name = section_name
            section.put()
            utils.log(section_name + ' added', type='S')

    def toggle_section(self, course, section_name):
        """
        Toggles the status of a section between Active and Inactive.

        Args:
            course (object):
                Course under which this section exists
            section_name (str):
                Name of the section to be toggled.

        """
        section = models.Section.get_by_id(section_name, parent=course.key)
        if section:
            section.is_active = not section.is_active
            section.put()
            utils.log('Status changed for ' + section_name, type='S')
        else:
            utils.error('Section ' + section_name + ' not found', handler=self)

    def post(self):
        """
        HTTP POST method to add a section to a course.
        """
        role, instructor = utils.get_role_user()
        if instructor and role == models.Role.instructor:
            course_name = self.request.get('course')
            section_name = self.request.get('section')
            action = self.request.get('action')

            if course_name and section_name and action:
                course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
                if course and course.is_active:
                    if action == 'add':
                        self.add_section(course, section_name.upper())
                    elif action == 'toggle':
                        self.toggle_section(course, section_name.upper())
                    else:
                        utils.error('Unexpected action:' + action, handler=self)
                else:
                    utils.error(course_name + ' does not exist OR is not active!', handler=self)
            else:
                utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            utils.error('user is null or not instructor', handler=self)

    def get(self):
        self.redirect('/courses')


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
            emails (str):
                Emails (IDs) of students to be added.

        """

        for email in emails:
            email = email.lower()
            student_emails = [s.email for s in section.students]
            if email not in student_emails:
                info = models.StudentInfo()
                info.email = email
                section.students.append(info)
            student = models.Student.get_by_id(email)
            if not student:
                student = models.Student(id=email)
                student.email = email
            if section.key not in student.sections:
                student.sections.append(section.key)
            student.put()
        section.put()
        utils.log('Students added to Section ' + str(section), type='S')

    def remove_student(self, section, email):
        """
        Removes a specific students from the given section.

        Args:
            section (object):
                Section from which the student is to be removed.
            email (str):
                Email (ID) of the student to be removed.

        """
        student = models.Student.get_by_id(email)
        if student:
            section.students = [s for s in section.students if s.email != email]  # TODO better? use remove?
            if section.key in student.sections:
                student.sections.remove(section.key)
            student.put()
            section.put()
            utils.log(
                    'Student {0} has been removed from Section {1}'.format(str(student), str(section)), handler=self,
                    type='S')
        else:
            utils.error('Student does not exist!', handler=self)

    def post(self):
        """
        HTTP POST method to add the student.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            course_name = self.request.get('course')
            section_name = self.request.get('section')
            action = self.request.get('action')

            if course_name and section_name and action:
                course = models.Course.get_by_id(course_name.upper(), parent=user.key)
                if course:
                    section = models.Section.get_by_id(section_name.upper(), parent=course.key)
                    if section:
                        if action == 'add':
                            emails = json.loads(self.request.get('emails'))  # retrieve emails
                            self.add_students(section, emails)
                        elif action == 'remove':
                            email = self.request.get('email').lower()
                            self.remove_student(section, email)
                        else:
                            utils.error('Unexpected action: ' + action, handler=self)
                    else:
                        utils.error(section_name + ' section does not exist!', handler=self)
                else:
                    utils.error(course_name + ' course does not exist!', handler=self)
            else:
                utils.error('Invalid arguments: course_name or section_name or actoin is null', handler=self)
        else:
            utils.error('user is null or not instructor', handler=self)
            self.redirect('/')

    def get(self):
        """
        HTTP GET method to retrieve the list of students from the datastore.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            course_name = self.request.get('course')
            selected_section_name = self.request.get('section')
            template_values = utils.get_courses_and_sections(user, course_name.upper(), selected_section_name.upper())
            template_values['logouturl'] = logout_url
            template = utils.jinja_env().get_template('instructor_list_students.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user null or not instructor', handler=self)
            self.redirect('/')


class Rounds(webapp2.RequestHandler):
    """
    API to retrieve and display the information of *rounds* for the selected course and section.

    By default, the alphabetically first course and first section is selected.
    To look at the rounds for other course/sections, the user can select from the given drop down list.
    """

    def get(self):
        """
        HTTP GET method to retrieve the rounds.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            course_name = self.request.get('course')
            selected_section_name = self.request.get('section')
            template_values = utils.get_courses_and_sections(user, course_name.upper(), selected_section_name.upper())
            if 'selectedSectionObject' in template_values:
                current_section = template_values['selectedSectionObject']
                template_values['activeRound'] = current_section.current_round
                rounds = models.Round.query(ancestor=current_section.key).fetch()
                if rounds:
                    template_values['rounds'] = rounds
                    discussion_rounds = []
                    for r in rounds:
                        if r.number == 1:
                            template_values['leadInQuestion'] = r
                        elif r.is_quiz:
                            template_values['summaryQuestion'] = r
                        else:
                            discussion_rounds.append(r)
                    template_values['discussionRounds'] = discussion_rounds
                if 'summaryQuestion' in template_values:
                    template_values['nextRound'] = current_section.rounds
                else:
                    template_values['nextRound'] = current_section.rounds + 1
            template_values['logouturl'] = logout_url
            template = utils.jinja_env().get_template('instructor_rounds.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user null or not instructor', handler=self)
            self.redirect('/')

    def add_round(self, section):
        curr_round = int(self.request.get('round'))
        time = self.request.get('time')

        round_obj = models.Round(parent=section.key, id=curr_round)
        round_obj.deadline = time
        round_obj.number = curr_round

        round_type = self.request.get('roundType')
        if round_type == 'leadin' or round_type == 'summary':
            question = self.request.get('question')

            round_obj.is_quiz = True
            num_options = int(self.request.get('number'))
            options = json.loads(self.request.get('options'))
            round_obj.quiz = models.Question(options_total=num_options, question=question,
                                             options=options)
        elif round_type == 'discussion':
            description = self.request.get('description')
            round_obj.description = description
        else:
            utils.error('Unknown round_type passed.', handler=self)
        round_obj.put()
        # Only update the value of total rounds if a new round is created,
        # not when we edit an old round is edited
        if curr_round > section.rounds:
            section.rounds = curr_round
            section.put()
        utils.log('Success, round added.', type='S', handler=self)

    def activate_round(self, section):
        next_round = int(self.request.get('round'))
        if section.current_round != next_round:
            # If the selected round is not currently active make it active
            section.current_round = next_round
            section.put()
            utils.log('Success, round active.', type='S', handler=self)

    def post(self):
        """
        HTTP POST method to add the round.
        """

        # TODO Markdown support
        # TODO Time picker suitable to all browsers (currently works only on Chrome)
        # TODO Timezone support in deadlines

        role, instructor = utils.get_role_user()
        if instructor and role == models.Role.instructor:
            course_name = self.request.get('course').upper()
            section_name = self.request.get('section').upper()
            action = self.request.get('action')

            # get course and section from datastore
            if course_name and section_name and action:
                course = models.Course.get_by_id(course_name, parent=instructor.key)
                if course:
                    section = models.Section.get_by_id(section_name, parent=course.key)
                    if section:
                        if action == 'add':
                            self.add_round(section)
                        elif action == 'activate':
                            self.activate_round(section)
                        else:
                            utils.error('Unexpected action: ' + action, handler=self)
                    else:
                        utils.error('Section {s} does not exist!'.format(s=section_name), handler=self)
                else:
                    utils.error('Course {c} does not exist!'.format(c=course_name), handler=self)
            else:
                utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            utils.error('user null or not instructor', handler=self)
            self.redirect('/')


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
        if group_count:
            if section.groups != group_count and group_count > 0:
                # If the total number of groups are not as requested change them
                section.groups = group_count
                section.put()
            utils.log('Groups modified.', type='S', handler=self)
        else:
            utils.error('Groups count not available.', handler=self)

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
        if groups:
            for student in section.students:
                if student.email in groups:
                    student.group = int(groups[student.email])
                    group = models.Group.get_by_id(student.group, parent=section.key)
                    if not group:
                        group = models.Group(parent=section.key, id=student.group)
                        group.number = student.group
                    if student.email not in group.members:
                        group.members.append(student.email)
                        group.size += 1
                        student.alias = 'S' + str(group.size)
                        group.put()
            section.put()
            utils.log('Groups updated.', handler=self)
        else:
            utils.error('Groups information not available.', handler=self)

    def get(self):
        """
        HTTP GET Method to render the ``/groups`` page for the logged in Instructor.

        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            course_name = self.request.get('course')
            selected_section_name = self.request.get('section')

            template_values = utils.get_courses_and_sections(user, course_name.upper(),
                                                             selected_section_name.upper())
            if 'selectedSectionObject' in template_values:
                current_section = template_values['selectedSectionObject']
                if current_section.rounds > 0:
                    response = models.Response.query(
                            ancestor=models.Round.get_by_id(1, parent=current_section.key).key).fetch()
                    groups = current_section.groups
                    student = current_section.students
                    for res in response:
                        for stu in student:
                            if res.student == stu.email:
                                res.group = stu.group
                    template_values['responses'] = response
                    template_values['group'] = groups
            template_values['logouturl'] = logout_url
            template = utils.jinja_env().get_template('instructor_groups.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user not instructor', handler=self)
            self.redirect('/')

    def post(self):
        """
        HTTP POST method to create groups.
        """
        role, instructor = utils.get_role_user()
        if instructor and role == models.Role.instructor:
            course_name = self.request.get('course')
            section_name = self.request.get('section')
            action = self.request.get('action')
            if course_name and section_name and action:
                course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
                if course:
                    section = models.Section.get_by_id(section_name.upper(), parent=course.key)
                    if section:
                        utils.log('action = ' + action)
                        if action == 'add':
                            group_count = int(self.request.get('groups'))
                            self.modify_group_count(section, group_count)
                        elif action == 'update':
                            groups = json.loads(self.request.get('groups'))
                            self.update_groups(section, groups)
                        else:
                            utils.error('Unknown action' + action if action else 'None', handler=self)
                    else:
                        utils.error(section_name + ' section does not exist!', handler=self)
                else:
                    utils.error(course_name + ' course does not exist!', handler=self)
            else:
                utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            utils.error('user is null or not instructor', handler=self)
            self.redirect('/')


class Responses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, tabbed into different rounds.
    """

    def get(self):
        """
        HTTP GET method to retrieve the responses.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            course_name = self.request.get('course')
            selected_section_name = self.request.get('section')
            template_values = utils.get_courses_and_sections(user, course_name.upper(),
                                                             selected_section_name.upper())
            if 'selectedSectionObject' in template_values:
                current_section = template_values['selectedSectionObject']
                template_values['round'] = current_section.rounds
                resp = {}
                for i in range(1, current_section.rounds + 1):
                    response = models.Response.query(
                            ancestor=models.Round.get_by_id(i, parent=current_section.key).key).fetch()
                    # response is a list of all the responses for the round i
                    if response:
                        resp[str(i)] = response
                template_values['responses'] = resp
            template_values['logouturl'] = logout_url
            template = utils.jinja_env().get_template('instructor_responses.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user is null or not instructor', handler=self)
            self.redirect('/')


class GroupResponses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, organized into groups.
    """

    def get(self):
        """
        HTTP GET method to retrieve the group responses.
        """
        role, user = utils.get_role_user()
        if user and role == models.Role.instructor:
            logout_url = users.create_logout_url(self.request.uri)
            course_name = self.request.get('course')
            selected_section_name = self.request.get('section')
            template_values = utils.get_courses_and_sections(user, course_name.upper(),
                                                             selected_section_name.upper())
            if 'selectedSectionObject' in template_values:
                current_section = template_values['selectedSectionObject']
                template_values['round'] = current_section.rounds
                template_values['groups'] = current_section.groups
                if current_section.groups > 0:
                    resp = {}
                    for g in range(1, current_section.groups + 1):
                        for r in range(1, current_section.rounds + 1):
                            resp['group_' + str(g) + '_' + str(r)] = []
                    for r in range(1, current_section.rounds + 1):
                        responses = models.Response.query(
                                ancestor=models.Round.get_by_id(r, parent=current_section.key).key).fetch()
                        if responses:
                            for res in responses:
                                for s in current_section.students:
                                    if s.email == res.student and s.group != 0:
                                        res.alias = s.alias
                                        resp['group_' + str(s.group) + '_' + str(r)].append(res)
                                        break
                    template_values['responses'] = resp
            template_values['logouturl'] = logout_url
            template = utils.jinja_env().get_template('instructor_groups_responses.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user is null or not instructor', handler=self)
            self.redirect('/')
