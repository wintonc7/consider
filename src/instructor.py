"""
instructor.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 25, 2015

--------------------


"""
import json
import logging

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
            instructor: Instructor who is adding the course.
            course_name: Name of the course; must be unique across the app.

        """
        if course_name:
            course_name = course_name.upper()
            course = models.Course.get_by_id(course_name, parent=instructor.key)
            if course:
                self.response.write('E' + course_name + ' already exists!')
            else:
                course = models.Course(parent=instructor.key, id=course_name)
                course.name = course_name
                course.put()
                self.response.write("S" + course_name + " added.")
        else:
            self.response.write("Error! invalid arguments.")

    def toggle_course(self, instructor, course_name):
        """
        Toggles the status of a course between Active and Inactive.

        Args:
            instructor: Instructor whose course is to be toggled.
            course_name: Name of the course to be toggled.

        """
        if course_name:
            logging.info("Changing status of the Course: " + course_name)
            course = models.Course.get_by_id(course_name, parent=instructor.key)
            if course:
                course.is_active = not course.is_active
                course.put()
                self.response.write("Status changed for " + course_name)
            else:
                self.response.write("Course not found in the database.")
        else:
            self.response.write("Error! invalid arguments.")

    def post(self):
        """
        HTTP POST method for handling course requests.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('name')
                action = self.request.get('action')
                logging.info('Courses/ POST / course: ' + course_name + ', action: ' + action)

                if action == 'add':
                    self.add_course(result, course_name)
                elif action == 'toggle':
                    self.toggle_course(result, course_name)
            else:
                logging.error('Instructor expected [instructor.Courses.post]')
        else:
            logging.error('User expected [instructor.Courses.post]')


class Section(webapp2.RequestHandler):
    """
    Handles requests for managing sections: adding a section, toggling its status, etc.
    """

    def add_section(self, course, section_name):
        """
        Adds a section to the given course in the datastore.

        Args:
            course: Course to which the section is to be added.
            section_name: Name of the section; must be unique within the course.

        """
        section = models.Section.get_by_id(section_name, parent=course.key)
        if section:
            self.response.write("E" + section_name + " already exist!")
        else:
            section = models.Section(parent=course.key, id=section_name)
            section.name = section_name
            section.put()
            self.response.write("S" + section_name + " added.")

    def toggle_section(self, course, section_name):
        """
        Toggles the status of a section between Active and Inactive.

        Args:
            course: Course under which this section exists
            course_name: Name of the section to be toggled.

        """
        section = models.Section.get_by_id(section_name, parent=course.key)
        if section:
            section.is_active = not section.is_active
            section.put()
            self.response.write("Status changed for " + section_name)
        else:
            self.response.write("E" + "Section not found in the database.")

    def post(self):
        """
        HTTP POST method to add a section to a course.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                section_name = self.request.get('section').upper()
                course_name = self.request.get('course').upper()
                action = self.request.get('action')

                if course_name:
                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course and course.is_active:
                        if action == 'add':
                            self.add_section(course, section_name)
                        elif action == 'toggle':
                            self.toggle_section(course, section_name)
                        else:
                            self.response.write('E' + 'Wrong action!!')
                    else:
                        self.response.write("E" + course_name + " course does not exist OR is not active!")
                else:
                    self.response.write("E" + "No valid course_name found.")
            else:
                self.response.write("Error! invalid arguments.")


class Students(webapp2.RequestHandler):
    """
    API to add a student to the given section and course.
    """

    def add_students(self, section, emails):
        """
        Adds one or more students to the given section in the datastore.

        Args:
            section: Section to which the studetns are to be added.
            emails: Emails (IDs) of students to be added.

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
        logging.info("Students added to Section " + str(section))

    def remove_student(self, section, email):
        """
        Removes a specific students from the given section.

        Args:
            section: Section from which the student is to be removed.
            email: Email (ID) of the student to be removed.

        """
        student = models.Student.get_by_id(email)
        if student:
            section.students = [s for s in section.students if s.email != email]
            if section.key in student.sections:
                student.sections.remove(section.key)
            student.put()
            section.put()
            logging.info(
                    "Student" + str(student) + " has been removed from Section " + str(section))
            self.response.write("S" + "Student removed from section.")
        else:
            self.response.write("E" + "Student does not exist!")

    def post(self):
        """
        HTTP POST method to add the student.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('course').upper()
                section_name = self.request.get('section').upper()
                action = self.request.get('action')

                if course_name and section_name:

                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = models.Section.get_by_id(section_name, parent=course.key)
                        if section:

                            if action == 'add':
                                emails = json.loads(self.request.get('emails'))  # retrieve emails
                                self.add_students(section, emails)
                            elif action == 'remove':
                                email = self.request.get('email').lower()
                                self.remove_student(section, email)
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")

    def get(self):
        """
        HTTP GET method to retrieve the list of students from the datastore.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is models.Instructor:
                    logging.info('Instructor navigated to Students ' + str(result))
                    course_name = self.request.get('course')
                    selected_section = self.request.get('section')
                    template_values = utils.get_courses_and_sections(result, course_name, selected_section)
                    template_values['logouturl'] = url
                    template = utils.jinja_env().get_template('list_students.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
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
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is models.Instructor:
                    course_name = self.request.get('course')
                    selected_section = self.request.get('section')
                    template_values = utils.get_courses_and_sections(result, course_name, selected_section)
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
                    template_values['logouturl'] = url
                    template = utils.jinja_env().get_template('rounds.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class AddRound(webapp2.RequestHandler):
    """
    API to add a round to the section.

    Pops open a new ``modal`` which asks for the details of the round, including deadline and question.

    """

    def post(self):
        """
        HTTP POST method to add the round.
        """

        # TODO Markdown support
        # TODO Time picker suitable to all browsers (currently works only on Chrome)
        # TODO Timezone support in deadlines

        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                time = self.request.get('time')
                question = self.request.get('question')
                description = self.request.get('description')
                curr_round = int(self.request.get('round'))
                is_last_round = bool(self.request.get('isLastRound'))
                if course_name and section_name and time and (question or description) and curr_round and str(
                        is_last_round):
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = models.Section.get_by_id(section_name, parent=course.key)
                        if section:
                            round_obj = models.Round(parent=section.key, id=curr_round)
                            round_obj.deadline = time
                            round_obj.number = curr_round
                            if curr_round == 1 or is_last_round:
                                # It is either Lead-in question or summary question
                                round_obj.is_quiz = True
                                number_options = int(self.request.get('number'))
                                options = json.loads(self.request.get('options'))
                                round_obj.quiz = models.Question(options_total=number_options, question=question,
                                                                 options=options)
                            else:
                                round_obj.description = description
                            round_obj.put()
                            # Only update the value of total rounds if a new round is created,
                            # not when we edit an old round is edited
                            if curr_round > section.rounds:
                                section.rounds = curr_round
                                section.put()
                            self.response.write("S" + "Success, round added.")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class ActivateRound(webapp2.RequestHandler):
    """
    API to activate a particular round for this section.

    The instructor can add rounds in advance, but has to activate each round when it is supposed to start.
    """

    def post(self):
        """
        HTTP POST method to activate the round.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                next_round = int(self.request.get('round'))
                if course_name and section_name and next_round:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = models.Section.get_by_id(section_name, parent=course.key)
                        if section:
                            if section.current_round != next_round:
                                # If the selected round is not currently active make it active
                                section.current_round = next_round
                                section.put()
                            self.response.write("S" + "Success, round active.")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class Groups(webapp2.RequestHandler):
    """
    API to retrieve and display the information of groups formed for the selected course and section.

    """

    def get(self):
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = utils.get_courses_and_sections(result, course_name, selected_section)
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
                template_values['logouturl'] = url
                template = utils.jinja_env().get_template('groups.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class AddGroups(webapp2.RequestHandler):
    """
    API to organize students in to groups.

    The user (instructor) can modify the number of groups and then assign each student to one of the groups.
    """

    def post(self):
        """
        HTTP POST method to create groups.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                groups = int(self.request.get('groups'))
                if course_name and section_name and groups:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = models.Section.get_by_id(section_name, parent=course.key)
                        if section:
                            if section.groups != groups and groups > 0:
                                # If the total number of groups are not as requested change them
                                section.groups = groups
                                section.put()
                            self.response.write("S" + "Groups modified.")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class UpdateGroups(webapp2.RequestHandler):
    """
    API to update the group assignments.

    The user (instructor) can reassign groups using this API.
    """

    def post(self):
        """
        HTTP POST method to update the groups.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                groups = json.loads(self.request.get('groups'))
                if course_name and section_name and groups:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = models.Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = models.Section.get_by_id(section_name, parent=course.key)
                        if section:
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
                            self.response.write("S" + "Groups updated.")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class Responses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, tabbed into different rounds.
    """

    def get(self):
        """
        HTTP GET method to retrieve the responses.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = utils.get_courses_and_sections(result, course_name, selected_section)
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
                template_values['logouturl'] = url
                template = utils.jinja_env().get_template('responses.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class GroupResponses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, organized into groups.
    """

    def get(self):
        """
        HTTP GET method to retrieve the group responses.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result and type(result) is models.Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = utils.get_courses_and_sections(result, course_name, selected_section)
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
                template_values['logouturl'] = url
                template = utils.jinja_env().get_template('groups_responses.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')
