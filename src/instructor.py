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
        # Start by trying to grab the course from the database
        course = models.Course.get_by_id(course_name, parent=instructor.key)
        # Check to see if it already exists
        if course:
            # And error if so
            utils.error(course_name + ' already exists', handler=self)
        else:
            # Otherwise, create it, store it in the database, and log it
            course = models.Course(parent=instructor.key, id=course_name)
            course.name = course_name
            course.put()
            utils.log(course_name + ' added', type='S',handler=self)
        #end
    #end add_course

    def toggle_course(self, instructor, course_name):
        """
        Toggles the status of a course between Active and Inactive.

        Args:
            instructor (object):
                Instructor whose course is to be toggled.
            course_name (str):
                Name of the course to be toggled.

        """
        # First, grab the course from the database
        course = models.Course.get_by_id(course_name, parent=instructor.key)
        if course:
            course.is_active = not course.is_active
            course.put()
            utils.log('Status changed for ' + course_name, type='S',handler=self)
        else:
            utils.error('Course ' + course_name + ' not found', handler=self)
        #end
    #end toggle_course

    def post(self):
        """
        HTTP POST method for handling course requests.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

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
                self.add_course(instructor, course_name.upper())
            elif action == 'toggle':
                # Or toggle if toggle
                self.toggle_course(instructor, course_name.upper())
            else:
                # If any other action, log it as an error
                utils.error('Unexpected action: ' + action,handler=self)
            #end
        #end
    #end post

    def get(self):
        """
        Display the Course list for this Instructor.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Otherwise, generate a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Log that the current instructor is logged in
        utils.log('Instructor logged in ' + str(instructor))
        # And start building the template values
        template_values = {'logouturl': logout_url, 'expand': self.request.get('course')}
        # Grab the list of courses attributed to the logged in instructor
        courses = models.Course.query(ancestor=instructor.key).fetch()
        # Double check that they actually have courses
        if courses:
            # Then loop over them
            for course in courses:
                # And grab all the sections attributed to that course
                course.sections = models.Section.query(ancestor=course.key).fetch()
            #end
            # Add all the instructor's courses to the template values
            template_values['courses'] = courses
        #end
        # And set the template and render the page
        template = utils.jinja_env().get_template('instructor_courses.html')
        self.response.write(template.render(template_values))
    #end get

#end class Courses


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
        # First, start by grabbing the section passed in from the database
        section = models.Section.get_by_id(section_name, parent=course.key)
        # Double check that it doesn't already exist
        if section:
            # And send an error if it does
            utils.error(section_name + ' already exists', handler=self)
        else:
            # Otherwise, create it, save it to the database, and log it
            section = models.Section(parent=course.key, id=section_name)
            section.name = section_name
            section.put()
            utils.log(section_name + ' added', type='S')
        #end
    #end add_section

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
        section = models.Section.get_by_id(section_name, parent=course.key)
        # Double check that it actually exists
        if section:
            # Toggle the section to active, save it to the database, and log it
            section.is_active = not section.is_active
            section.put()
            utils.log('Status changed for ' + section_name, type='S')
        else:
            # Send an error if the section passed in doesn't exist
            utils.error('Section ' + section_name + ' not found', handler=self)
        #end
    #end toggle_section

    def post(self):
        """
        HTTP POST method to add a section to a course.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

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
            course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
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
                #end
            #end
        #end
    #end post

    def get(self):
        self.redirect('/courses')
    #end get

#end class Section


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
        # Start by looping over the list of emails supplied
        for email in emails:
            # Transform the supplied email to lowercase
            email = email.lower()
            # Then make a list of all the emails currently in the section
            student_emails = [s.email for s in section.students]
            # Check that the supplied email isn't already in the section
            if email not in student_emails:
                # And add them to the list of students for the section
                info = models.StudentInfo()
                info.email = email
                section.students.append(info)
            #end
            # Now grab the student from the database
            student = models.Student.get_by_id(email)
            # And if they don't already have a db entry
            if not student:
                # Create a new student and assign the email address
                student = models.Student(id=email)
                student.email = email
            #end
            # Now check if the current student is subscribed to this section
            if section.key not in student.sections:
                # And add them if they weren't already
                student.sections.append(section.key)
            #end
            # Save the student data back to the database
            student.put()
        #end
        # Now save all the section data back to the database and log it
        section.put()
        utils.log('Students added to Section ' + str(section), type='S')
    #end add_students

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
        student = models.Student.get_by_id(email)
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
            #end
            # And save both the student and section back to the db and log it
            student.put()
            section.put()
            utils.log(
                    'Student {0} has been removed from Section {1}'.format(str(student),
                    str(section)), handler=self, type='S')
        #end
    #end remove_student

    def post(self):
        """
        HTTP POST method to add the student.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Now grab the course, section, and action from the webpage
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        action = self.request.get('action')
        # Check that all three were actually supplied
        if not course_name or not section_name or not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or actoin is null', handler=self)
        else:
            # Now try to grab the course from the database
            course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
            # Check if it already exists
            if not course:
                # Error if it doesn't
                utils.error(course_name + ' course does not exist!', handler=self)
            else:
                # Now grab the section from the database
                section = models.Section.get_by_id(section_name.upper(), parent=course.key)
                if not section:
                    # And error if it doesn't exist
                    utils.error(section_name + ' section does not exist!', handler=self)
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
                    #end
                #end
            #end
        #end
    #end post

    def get(self):
        """
        HTTP GET method to retrieve the list of students from the datastore.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Get the course and section name from the webpage
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And start building the template values
        template_values = utils.get_courses_and_sections(instructor, course_name.upper(), selected_section_name.upper())
        template_values['logouturl'] = logout_url
        # Set the template and render the page
        template = utils.jinja_env().get_template('instructor_list_students.html')
        self.response.write(template.render(template_values))
    #end get

#end class Students

class RoundsTest(webapp2.RequestHandler):
    def get(self):
        role, user = utils.get_role_user()
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        template_values = utils.get_courses_and_sections(user, course_name.upper(), selected_section_name.upper())
        template = utils.jinja_env().get_template('instructor/rounds_test.html')
        self.response.write(template.render(template_values))

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
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Now create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Grab the course and section name from the webpage
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And get all the courses and sections for this instructor
        template_values = utils.get_courses_and_sections(instructor, course_name.upper(), selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # Set the current active round
            template_values['activeRound'] = current_section.current_round
            # And grab all the rounds for this section
            rounds = models.Round.query(ancestor=current_section.key).fetch()
            # Double check that there are actually rounds already created
            if rounds:
                # And set the template values
                template_values['rounds'] = rounds
                # Create an empty list to hold the discussion rounds
                discussion_rounds = []
                # And loop over all of the rounds for this section
                for r in rounds:
                    # Set the lead-in question
                    if r.number == 1:
                        template_values['leadInQuestion'] = r
                    elif r.is_quiz:
                        # And if not the lead-in question, but still a quiz
                        # it must be the summary round
                        template_values['summaryQuestion'] = r
                    else:
                        # Otherwise, it's just a discussion round
                        discussion_rounds.append(r)
                    #end
                #end
                # Set the discussion round template values
                template_values['discussionRounds'] = discussion_rounds
            #end
            # Check to see if the summary round was set in the template
            if 'summaryQuestion' in template_values:
                # If so, set the next round to the total number of rounds
                template_values['nextRound'] = current_section.rounds
            else:
                # Otherwise, it must be set to the number of rounds plus
                # one (to account for the eventual summary round)
                template_values['nextRound'] = current_section.rounds + 1
            #end
        #end
        # Set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor_rounds.html')
        self.response.write(template.render(template_values))
    #end get

    def add_round(self, section):
        # Grab the current round and time from the webpage
        curr_round = int(self.request.get('round'))
        time = self.request.get('time')
        #Create a new round object with those parameters
        round_obj = models.Round(parent=section.key, id=curr_round)
        round_obj.deadline = time
        round_obj.number = curr_round
        # Grab the type of round from the webpage
        round_type = self.request.get('roundType')
        # And check if it's a lead-in or summary round (i.e. a quiz)
        if round_type == 'leadin' or round_type == 'summary':
            # If so, grab the question from the form
            question = self.request.get('question')
            # Set the object to be a quiz type
            round_obj.is_quiz = True
            # And grab the number of options and list of options from the page
            num_options = int(self.request.get('number'))
            options = json.loads(self.request.get('options'))
            # And create and store the question
            round_obj.quiz = models.Question(options_total=num_options,
                                             question=question, options=options)
        elif round_type == 'discussion':
            # Otherwise, if the round is set as discussion,
            # Grab the description and anonymity settings from the page
            description = self.request.get('description')
            anonymity = self.request.get('anonymity')
            # And set those properties in the round object
            round_obj.description = description
            if anonymity != "yes":
                round_obj.is_anonymous = False
            #end
        else:
            # And send an error if any other round type is sent
            utils.error('Unknown round_type passed.', handler=self)
        #end
        # And save the round object into the database
        round_obj.put()
        # Only update the value of total rounds if a new round is created,
        # not when we edit an old round is edited
        if curr_round > section.rounds:
            section.rounds = curr_round
            section.put()
        #end
        utils.log('Success, round added.', type='S', handler=self)
    #end add_round

    def activate_round(self, section):
        # Grab the number for the next round from the page
        next_round = int(self.request.get('round'))
        if section.current_round != next_round:
            # If the selected round is not currently active make it active
            section.current_round = next_round
            section.put()
            utils.log('Success, round active.', type='S', handler=self)
        #end
    #end activate_round

    def post(self):
        """
        HTTP POST method to add the round.
        """

        # TODO Markdown support
        # TODO Timezone support in deadlines

        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Otherwise, grab the course name, section name, and action
        course_name = self.request.get('course').upper()
        section_name = self.request.get('section').upper()
        action = self.request.get('action')
        # Check that all three are supplied
        if not course_name or not section_name or not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            # Otherwise, grab the course from the database
            course = models.Course.get_by_id(course_name, parent=instructor.key)
            # And check that it actually exists
            if not course:
                # Error if not
                utils.error('Course {c} does not exist!'.format(c=course_name), handler=self)
            else:
                # Then grab the section from the database
                section = models.Section.get_by_id(section_name, parent=course.key)
                # And check that it actually exists
                if not section:
                    # Error if not
                    utils.error('Section {s} does not exist!'.format(s=section_name), handler=self)
                else:
                    # Switch on the action
                    if action == 'add':
                        # Add
                        self.add_round(section)
                    elif action == 'activate':
                        # Or turn on
                        self.activate_round(section)
                    else:
                        # And error if any other action is provided
                        utils.error('Unexpected action: ' + action, handler=self)
                    #end
                #end
            #end
        #end
    #end post

#end class Rounds


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
            #end
            utils.log('Groups modified.', type='S', handler=self)
        #end
    #end modify_group_count

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
                    group = models.Group.get_by_id(student.group, parent=section.key)
                    # Double check that it actually exists
                    if not group:
                        # And create it if not, giving it the proper number
                        group = models.Group(parent=section.key, id=student.group)
                        group.number = student.group
                    #end
                    # Now check if the student is listed in the correct group
                    if student.email not in group.members:
                        # If not, add that student in to the group
                        group.members.append(student.email)
                        # Update the size
                        group.size += 1
                        # Set the student's alias for that group
                        student.alias = 'S' + str(group.size)
                        # And commit the changes to the group
                        group.put()
                    #end
                #end
            #end
            # Commit the changes to the section and log it
            section.put()
            utils.log('Groups updated.', handler=self)
        #end
    #end update_groups

    def get(self):
        """
        HTTP GET Method to render the ``/groups`` page for the logged in Instructor.

        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And get the course and section names from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # Grab all the courses and sections for the logged in instructor
        template_values = utils.get_courses_and_sections(instructor,
                            course_name.upper(), selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # Check that the current section has at least one round
            if current_section.rounds > 0:
                # Grab the responses from the lead-in question
                response = models.Response.query(
                        ancestor=models.Round.get_by_id(1, parent=current_section.key).key).fetch()
                # Loop over the responses
                for res in response:
                    # And loop over the students in this section
                    for stu in current_section.students:
                        # And check when the response matches the student
                        if res.student == stu.email:
                            # And set the group of the response to the
                            # group of the student who made that response
                            res.group = stu.group
                        #end
                    #end
                #end
                # Add the responses and current group to the template values
                template_values['responses'] = response
                template_values['group'] = current_section.groups
            #end
        #end
        # Set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor_groups.html')
        self.response.write(template.render(template_values))
    #end get

    def post(self):
        """
        HTTP POST method to create groups.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Get the course and section name and the action from the page
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        action = self.request.get('action')
        # Check that all three are actually supplied
        if not course_name or not section_name or not action:
            # Error if not
            utils.error('Invalid arguments: course_name or section_name or action is null', handler=self)
        else:
            # Otherwise, grab the course from the database
            course = models.Course.get_by_id(course_name.upper(), parent=instructor.key)
            # Double check that it actually existed
            if not course:
                # Error if not
                    utils.error(course_name + ' course does not exist!', handler=self)
            else:
                # Now grab the section
                section = models.Section.get_by_id(section_name.upper(), parent=course.key)
                # And double check that it exists
                if not section:
                    #Error if not
                    utils.error(section_name + ' section does not exist!', handler=self)
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
                    #end
                #end
            #end
        #end
    #end post

#end class Groups


class Responses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, tabbed into different rounds.
    """

    def get(self):
        """
        HTTP GET method to retrieve the responses.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Create logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And grab the course and section name from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And grab all the other courses and sections for this instructor
        template_values = utils.get_courses_and_sections(instructor,
                            course_name.upper(), selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # And set the round
            template_values['round'] = current_section.rounds
            # Create a new dict for the responses
            resp = {}
            # And loop over the number of rounds (indexed at 1 for lead-in)
            for i in range(1, current_section.rounds + 1):
                response = models.Response.query(
                        ancestor=models.Round.get_by_id(i, parent=current_section.key).key).fetch()
                # response is a list of all the responses for the round i
                if response:
                    resp[str(i)] = response
                #end
            #end
            # Add the responses to the template values
            template_values['responses'] = resp
        #end
        # And set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor_responses.html')
        self.response.write(template.render(template_values))
    #end get

#end class Responses


class GroupResponses(webapp2.RequestHandler):
    """
    API to retrieve and display responses for each section, organized into groups.
    """

    def get(self):
        """
        HTTP GET method to retrieve the group responses.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_instructor_privilege()
        if not instructor:
            # Send them home and short circuit all other logic
            self.redirect('/')
            return
        #end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And get the course and section name from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And grab the other courses and sections from this instructor
        template_values = utils.get_courses_and_sections(instructor,
                            course_name.upper(), selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab the current section from the template values
            current_section = template_values['selectedSectionObject']
            # Set the rounds and groups
            template_values['round'] = current_section.rounds
            template_values['groups'] = current_section.groups
            # And check that groups have actually been assigned
            if current_section.groups > 0:
                # Create a new dict for responses
                resp = {}
                # Loop over the groups (indexed by 1)
                for g in range(1, current_section.groups + 1):
                    # And loop over the rounds (indexed by 1)
                    for r in range(1, current_section.rounds + 1):
                        # Now set an empty list for each group and round
                        resp['group_' + str(g) + '_' + str(r)] = []
                    #end
                #end
                # Loop over the number of rounds (indexed by 1)
                for r in range(1, current_section.rounds + 1):
                    # Grab the responses for that round from the db
                    responses = models.Response.query(
                            ancestor=models.Round.get_by_id(r, parent=current_section.key).key).fetch()
                    # Double check that the responses actually exist
                    if responses:
                        # And loop over the responses
                        for res in responses:
                            # And loop over the students in this section
                            for s in current_section.students:
                                # Check that the email of the student
                                # and the email of the response match
                                # and that the student is in a group
                                if s.email == res.student and s.group != 0:
                                    # Set the alias of the response
                                    res.alias = s.alias
                                    # Append the response to the appropriate
                                    # group and round
                                    resp['group_' + str(s.group) + '_' + str(r)].append(res)
                                    break
                                #end
                            #end
                        #end
                    #end
                #end
                # And set the template values for all the responses
                template_values['responses'] = resp
            #end
        #end
        # And set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor_groups_responses.html')
        self.response.write(template.render(template_values))
    #end get

#end class GroupResponses

