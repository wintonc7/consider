import os
import webapp2
import jinja2
import logging
import json
import datetime

from google.appengine.api import users
from google.appengine.ext import vendor

from models import *

vendor.add('libs')

import markdown

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

errorCodes = {
    '100': "Oops! Something went wrong please try again.",
    '101': "Sorry you are not registered with this application, please contact your Instructor.",
    '102': "Sorry you are not an instructor.",
    '103': "Sorry no rounds are active for this section, please try again later.",
    '104': "Sorry the round was not found, please contact your Instructor.",
    '105': "Sorry, your group was not found, please contact your Instructor."
}


def get_role(user):
    if user:
        result = Instructor.query(Instructor.email == user.email()).get()
        if result:
            return result
        else:
            result = Student.query(Student.email == user.email()).get()
            if result:
                return result
    return False


class ErrorPage(webapp2.RequestHandler):
    """Page to display errors"""

    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            template_values = {
                'url': url
            }
            error = self.request.get('code')
            message = None
            if error:
                if error in errorCodes:
                    message = errorCodes[error]
            if not message:
                message = errorCodes['100']
            template_values['text'] = message
            template = JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect('/')


class AddCourse(webapp2.RequestHandler):
    """Adding course to the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('name')
                if course_name:
                    course_name = course_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        self.response.write("E" + course_name + " already exist!")
                    else:
                        course = Course(parent=result.key, id=course_name)
                        course.name = course_name
                        course.put()
                        self.response.write("S" + course_name + " added.")
                else:
                    self.response.write("Error! invalid arguments.")


class ToggleCourse(webapp2.RequestHandler):
    """Changing status of Course in the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                if course_name:
                    logging.info("Changing status of " + course_name)
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        course.is_active = not course.is_active
                        course.put()
                        self.response.write("Status changed for " + course_name)
                    else:
                        self.response.write("Course not found in the database.")
                else:
                    self.response.write("Error! invalid arguments.")


class AddSection(webapp2.RequestHandler):
    """Adding section to a course in the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                section_name = self.request.get('name')
                course_name = self.request.get('course')
                if course_name and section_name:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
                        if section:
                            self.response.write("E" + section_name + " already exist!")
                        else:
                            section = Section(parent=course.key, id=section_name)
                            section.name = section_name
                            section.put()
                            self.response.write("S" + section_name + " added.")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("Error! invalid arguments.")


class ToggleSection(webapp2.RequestHandler):
    """Changing status of Section for a Course in the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                if course_name and section_name:
                    logging.info("Changing status of " + section_name + " for course " + course_name)
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        if course.is_active:
                            section = Section.get_by_id(section_name, parent=course.key)
                            if section:
                                section.is_active = not section.is_active
                                section.put()
                                self.response.write("Status changed for " + section_name)
                            else:
                                self.response.write("E" + "Section not found in the database.")
                        else:
                            self.response.write("E" + "Status cannot be changed, please activate " + course_name)
                    else:
                        self.response.write("E" + "Course not found in the database.")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class MainPage(webapp2.RequestHandler):
    """Main function that will handle the first request"""

    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/home')
        else:
            url = users.create_login_url(self.request.uri)
            template_values = {
                'url': url
            }
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))


class HomePage(webapp2.RequestHandler):
    """Redirecting accordingly based on email"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is Instructor:
                    # Show instructor console
                    logging.info('Instructor logged in ' + str(result))
                    template_values = {'logouturl': url, 'expand': self.request.get('course')}
                    courses = Course.query(ancestor=result.key).fetch()
                    if courses:
                        for course in courses:
                            course.sections_all = Section.query(ancestor=course.key).fetch()
                            course.sections = len(course.sections_all)
                        template_values['courses'] = courses
                    template = JINJA_ENVIRONMENT.get_template('course.html')
                    self.response.write(template.render(template_values))
                elif type(result) is Student:
                    logging.info('Student logged in ' + str(result))
                    template_values = {'logouturl': url, 'nickname': user.nickname()}
                    sections = result.sections
                    section_list = []
                    if sections:
                        for section in sections:
                            section_obj = section.get()
                            course_obj = section.parent().get()
                            if section_obj and course_obj:
                                sec = {
                                    'key': section.urlsafe(),
                                    'name': section_obj.name,
                                    'course': course_obj.name
                                }
                                section_list.append(sec)
                    template_values['sections'] = section_list
                    template = JINJA_ENVIRONMENT.get_template('student_home.html')
                    self.response.write(template.render(template_values))
                else:
                    logging.info(str(result) + ' navigated to Error')
                    self.redirect('/error?code=101')
            else:
                self.redirect('/error?code=101')
        else:
            self.redirect('/')


def get_courses_and_sections(result, course_name, selected_section):
    template_values = {}
    courses = Course.query(ancestor=result.key).fetch()
    if courses:
        course = None
        template_values['courses'] = courses
        if course_name:
            course_name = course_name.upper()
            course = Course.get_by_id(course_name, parent=result.key)
        if not course:
            course = courses[0]
        sections = Section.query(ancestor=course.key).fetch()
        template_values['selectedCourse'] = course.name
        if not sections and not course_name:
            sections = Section.query(ancestor=courses[0].key).fetch()
        template_values['sections'] = sections
        if sections:
            section = None
            if selected_section:
                selected_section = selected_section.upper()
                section = Section.get_by_id(selected_section, parent=course.key)
            if not section:
                section = sections[0]
            template_values['selectedSection'] = section.name
            template_values['selectedSectionObject'] = section
            template_values['students'] = section.students
    return template_values


class StudentsPage(webapp2.RequestHandler):
    """Page for instructor to add students to a particular section"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is Instructor:
                    logging.info('Instructor navigated to Students ' + str(result))
                    course_name = self.request.get('course')
                    selected_section = self.request.get('section')
                    template_values = get_courses_and_sections(result, course_name, selected_section)
                    template_values['logouturl'] = url
                    template = JINJA_ENVIRONMENT.get_template('students.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class AddStudent(webapp2.RequestHandler):
    """Adding students to the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                emails = json.loads(self.request.get('emails'))
                if course_name and section_name and emails:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
                        if section:
                            for email in emails:
                                email = email.lower()
                                student_emails = [s.email for s in section.students]
                                if email not in student_emails:
                                    info = StudentInfo()
                                    info.email = email
                                    section.students.append(info)
                                student = Student.get_by_id(email)
                                if not student:
                                    student = Student(id=email)
                                    student.email = email
                                if section.key not in student.sections:
                                    student.sections.append(section.key)
                                student.put()
                            section.put()
                            logging.info("Students added to Section " + str(section))
                            self.response.write("S" + "Students added to section.")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class RemoveStudent(webapp2.RequestHandler):
    """Removing students to the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                email = self.request.get('email')
                if course_name and section_name and email:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
                        if section:
                            email = email.lower()
                            student = Student.get_by_id(email)
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
                                self.response.write("E" + student + " does not exist!")
                        else:
                            self.response.write("E" + section_name + " section does not exist!")
                    else:
                        self.response.write("E" + course_name + " course does not exist!")
                else:
                    self.response.write("E" + "Error! invalid arguments.")


class Rounds(webapp2.RequestHandler):
    """Handling rounds page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is Instructor:
                    course_name = self.request.get('course')
                    selected_section = self.request.get('section')
                    template_values = get_courses_and_sections(result, course_name, selected_section)
                    if 'selectedSectionObject' in template_values:
                        current_section = template_values['selectedSectionObject']
                        template_values['activeRound'] = current_section.current_round
                        rounds = Round.query(ancestor=current_section.key).fetch()
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
                    template = JINJA_ENVIRONMENT.get_template('rounds.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class AddRound(webapp2.RequestHandler):
    """Adding rounds in the database for a particular section"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                time = self.request.get('time')
                question = self.request.get('question')
                description = self.request.get('description')
                curr_round = int(self.request.get('round'))
                is_last_round = bool(self.request.get('isLastRound'))
                if course_name and section_name and time and (question or description) and curr_round and str(is_last_round):
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
                        if section:
                            round_obj = Round(parent=section.key, id=curr_round)
                            round_obj.deadline = time
                            round_obj.number = curr_round
                            if curr_round == 1 or is_last_round:
                                # It is either Lead-in question or summary question
                                round_obj.is_quiz = True
                                number_options = int(self.request.get('number'))
                                options = json.loads(self.request.get('options'))
                                round_obj.quiz = Question(options_total=number_options, question=question,
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
    """Activating a particular round for a section"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                next_round = int(self.request.get('round'))
                if course_name and section_name and next_round:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
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


class SectionPage(webapp2.RequestHandler):
    """Redirecting student based on the section they selected"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is Student:
                    logging.info('Student logged in ' + str(result))
                    section_key = self.request.get('section')
                    if section_key:
                        try:
                            section = ndb.Key(urlsafe=section_key).get()
                            if section:
                                if section.current_round == 0:
                                    self.redirect('/error?code=103')
                                else:
                                    curr_round = Round.get_by_id(section.current_round, parent=section.key)
                                    if curr_round:
                                        if not curr_round.is_quiz:
                                            self.redirect('/discussion?section=' + section_key)
                                            return
                                        deadline = datetime.datetime.strptime(curr_round.deadline, '%Y-%m-%dT%H:%M')
                                        current_time = datetime.datetime.now()
                                        template_values = {
                                            'url': url
                                        }
                                        response = Response.get_by_id(result.email, parent=curr_round.key)
                                        if response:
                                            template_values['option'] = response.option
                                            template_values['comment'] = response.comment
                                            if response.summary:
                                                template_values['summary'] = response.summary
                                        if deadline < current_time:
                                            template_values['expired'] = True
                                        template_values['deadline'] = curr_round.deadline
                                        template_values['question'] = curr_round.quiz.question
                                        template_values['options'] = curr_round.quiz.options
                                        template_values['number'] = curr_round.quiz.options_total
                                        template_values['sectionKey'] = section_key
                                        if curr_round.number != 1:
                                            template_values['last_round'] = True
                                        template = JINJA_ENVIRONMENT.get_template('home.html')
                                        self.response.write(template.render(template_values))
                                    else:
                                        self.redirect('/error?code=104')
                            else:
                                self.redirect('/home')
                        except Exception as e:
                            logging.error('Got exception: ' + e.message)
                            self.redirect('/home')
                    else:
                        self.redirect('/home')
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


def check_response(response):
    for i in range(1, len(response)):
        if response[i] not in ['support', 'neutral', 'disagree']:
            return True
    return False


class SubmitResponse(webapp2.RequestHandler):
    """Accept responses from students and save them in the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            student = get_role(user)
            if student and type(student) is Student:
                option = self.request.get('option').lower()
                comment = self.request.get('comm')
                summary = self.request.get('summary')
                res = self.request.get('response')
                section_key = self.request.get('section')
                if section_key:
                    try:
                        section = ndb.Key(urlsafe=section_key).get()
                        if section:
                            current_round = Round.get_by_id(section.current_round, parent=section.key)
                            if current_round:
                                response = Response(parent=current_round.key, id=student.email)
                                if current_round.is_quiz:
                                    if not (option and comment):
                                        self.response.write('Invalid Parameters!')
                                        return
                                    if current_round.number != 1 and not summary:
                                        self.response.write('Invalid Parameters!')
                                        return
                                    response.option = option
                                    if summary:
                                        response.summary = summary
                                else:
                                    res = json.loads(res)
                                    if not (res and comment) or check_response(res):
                                        self.response.write('Invalid Parameters!')
                                        return
                                    for i in range(1, len(res)):
                                        response.response.append(res[i])
                                deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                                current_time = datetime.datetime.now()
                                if deadline >= current_time:
                                    response.comment = comment
                                    response.student = student.email
                                    response.put()
                                    self.response.write('Thank you, your response have been saved and you can edit your response any time before the deadline.')
                                else:
                                    self.response.write('Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                            else:
                                self.response.write('Sorry! The round is not visible, please try again later.')
                        else:
                            self.response.write('Sorry! The section is not visible, please try again later.')
                    except:
                        self.response.write('Sorry! There was some error submitting your response please try again later.')
                else:
                    self.response.write('Invalid Parameters!')
            else:
                self.response.write('Sorry! You were not identified as a student, please try again later.')
        else:
            self.response.write('Sorry! User is not recognized, please try again later.')


class Discussion(webapp2.RequestHandler):
    """Redirecting accordingly based on email"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is Student:
                    logging.info('Student navigated to discussion ' + str(result))
                    section_key = self.request.get('section')
                    if section_key:
                        try:
                            section = ndb.Key(urlsafe=section_key).get()
                            if section:
                                if section.current_round == 0:
                                    self.redirect('/error?code=103')
                                else:
                                    if section.current_round == 1:
                                        self.redirect('/home')
                                        return
                                    requested_round = self.request.get('round')
                                    if requested_round:
                                        requested_round = int(requested_round)
                                    else:
                                        requested_round = section.current_round
                                    d_round = Round.get_by_id(requested_round, parent=section.key)
                                    if d_round:
                                        group = 0
                                        alias = None
                                        for stu in section.students:
                                            if stu.email == result.email:
                                                group = stu.group
                                                alias = stu.alias
                                                break
                                        if group != 0 and alias:
                                            group = Group.get_by_id(group, parent=section.key)
                                            if group:
                                                comments = []
                                                previous_round = Round.get_by_id(requested_round - 1, parent=section.key)
                                                for stu in group.members:
                                                    response = Response.get_by_id(stu, parent=previous_round.key)
                                                    if response:
                                                        for s in section.students:
                                                            if s.email == stu:
                                                                comment = {
                                                                    'alias': s.alias,
                                                                    'response': response.comment,
                                                                    'opinion': response.response
                                                                }
                                                                if response.option != 'NA':
                                                                    comment['option'] = previous_round.quiz.options[int(response.option[-1]) - 1]
                                                                comments.append(comment)
                                                                break
                                                template_values = {
                                                    'url': url,
                                                    'alias': alias,
                                                    'comments': comments
                                                }
                                                stu_response = Response.get_by_id(result.email, parent=d_round.key)
                                                if stu_response:
                                                    template_values['comment'] = stu_response.comment
                                                    template_values['response'] = ','.join(str(item) for item in stu_response.response)
                                                deadline = datetime.datetime.strptime(d_round.deadline, '%Y-%m-%dT%H:%M')
                                                current_time = datetime.datetime.now()
                                                if deadline < current_time or requested_round != section.current_round:
                                                    template_values['expired'] = True
                                                if d_round.is_quiz:
                                                    template_values['expired'] = True
                                                template_values['deadline'] = d_round.deadline
                                                template_values['rounds'] = section.current_round
                                                template_values['curr_page'] = requested_round
                                                template_values['description'] = d_round.description
                                                template_values['sectionKey'] = section_key
                                                template = JINJA_ENVIRONMENT.get_template('discussion.html')
                                                self.response.write(template.render(template_values))
                                            else:
                                                logging.error("Group not found for " + str(result) + " Section: " + str(section))
                                                self.redirect('/error?code=105')
                                        else:
                                            logging.error("Group not found for " + str(result) + " Section: " + str(section))
                                            self.redirect('/error?code=105')
                                    else:
                                        logging.info("Requested round not found for " + str(result) + " Section: " + str(section))
                                        self.redirect('/home')
                            else:
                                logging.info("Section not found for key: " + section_key)
                                self.redirect('/home')
                        except Exception as e:
                            logging.info("Found exception " + e.message)
                            self.redirect('/home')
                    else:
                        self.redirect('/home')
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class Groups(webapp2.RequestHandler):
    """Handling groups page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = get_courses_and_sections(result, course_name, selected_section)
                if 'selectedSectionObject' in template_values:
                    current_section = template_values['selectedSectionObject']
                    if current_section.rounds > 0:
                        response = Response.query(ancestor=Round.get_by_id(1, parent=current_section.key).key).fetch()
                        groups = current_section.groups
                        student = current_section.students
                        for res in response:
                            for stu in student:
                                if res.student == stu.email:
                                    res.group = stu.group
                        template_values['responses'] = response
                        template_values['group'] = groups
                template_values['logouturl'] = url
                template = JINJA_ENVIRONMENT.get_template('groups.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class AddGroups(webapp2.RequestHandler):
    """Adding students to the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                groups = int(self.request.get('groups'))
                if course_name and section_name and groups:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
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
    """Updating groups of students"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                course_name = self.request.get('course')
                section_name = self.request.get('section')
                groups = json.loads(self.request.get('groups'))
                if course_name and section_name and groups:
                    course_name = course_name.upper()
                    section_name = section_name.upper()
                    course = Course.get_by_id(course_name, parent=result.key)
                    if course:
                        section = Section.get_by_id(section_name, parent=course.key)
                        if section:
                            for student in section.students:
                                if student.email in groups:
                                    student.group = int(groups[student.email])
                                    group = Group.get_by_id(student.group, parent=section.key)
                                    if not group:
                                        group = Group(parent=section.key, id=student.group)
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
    """Handling responses page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = get_courses_and_sections(result, course_name, selected_section)
                if 'selectedSectionObject' in template_values:
                    current_section = template_values['selectedSectionObject']
                    template_values['round'] = current_section.rounds
                    resp = {}
                    for i in range(1, current_section.rounds + 1):
                        response = Response.query(ancestor=Round.get_by_id(i, parent=current_section.key).key).fetch()
                        # response is a list of all the responses for the round i
                        if response:
                            resp[str(i)] = response
                    template_values['responses'] = resp
                template_values['logouturl'] = url
                template = JINJA_ENVIRONMENT.get_template('responses.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class GroupResponses(webapp2.RequestHandler):
    """Handling groups_responses page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = get_role(user)
            if result and type(result) is Instructor:
                url = users.create_logout_url(self.request.uri)
                course_name = self.request.get('course')
                selected_section = self.request.get('section')
                template_values = get_courses_and_sections(result, course_name, selected_section)
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
                            responses = Response.query(ancestor=Round.get_by_id(r, parent=current_section.key).key).fetch()
                            if responses:
                                for res in responses:
                                    for s in current_section.students:
                                        if s.email == res.student and s.group != 0:
                                            res.alias = s.alias
                                            resp['group_' + str(s.group) + '_' + str(r)].append(res)
                                            break
                        template_values['responses'] = resp
                template_values['logouturl'] = url
                template = JINJA_ENVIRONMENT.get_template('groups_responses.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/error', ErrorPage),
    ('/home', HomePage),
    ('/add_course', AddCourse),
    ('/toggleCourse', ToggleCourse),
    ('/add_section', AddSection),
    ('/toggleSection', ToggleSection),
    ('/students', StudentsPage),
    ('/addRound', AddRound),
    ('/activateRound', ActivateRound),
    ('/discussion', Discussion),
    ('/responses', Responses),
    ('/group_responses', GroupResponses),
    ('/addStudent', AddStudent),
    ('/removeStudent', RemoveStudent),
    ('/section', SectionPage),
    ('/submitResponse', SubmitResponse),
    ('/groups', Groups),
    ('/rounds', Rounds),
    ('/addGroups', AddGroups),
    ('/updateGroups', UpdateGroups)
], debug=True)
