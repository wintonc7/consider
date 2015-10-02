import os
import webapp2
import jinja2
import logging
import json
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Course(ndb.Model):
    """A model for holding different sections inside a particular Instructor"""
    name = ndb.StringProperty(required=True)
    is_active = ndb.BooleanProperty(default=True, indexed=False)


class Section(ndb.Model):
    """A main model for a particular section which will be child of course"""
    name = ndb.StringProperty(required="True")
    groups = ndb.IntegerProperty(default=0, indexed=False)
    current_round = ndb.IntegerProperty(default=0, indexed=False)
    rounds = ndb.IntegerProperty(default=0, indexed=False)
    students = ndb.StringProperty(repeated=True, indexed=False)
    is_active = ndb.BooleanProperty(default=True, indexed=False)


class Instructor(ndb.Model):
    """A main model for representing admins"""
    email = ndb.StringProperty(required="True")
    is_active = ndb.BooleanProperty(default=True, indexed=False)


# TODO remove this data model
class Admin(ndb.Model):
    """A main model for representing admins"""
    email = ndb.StringProperty(required=True)


class Student(ndb.Model):
    """A student model for all the students"""
    email = ndb.StringProperty(required=True)
    alias = ndb.StringProperty(default='NA')
    group = ndb.IntegerProperty(default=0, indexed=False)
    sections = ndb.KeyProperty(kind=Section, repeated=True, indexed=False)


class Group(ndb.Model):
    """A model to hold the properties of groups of each class"""
    number = ndb.IntegerProperty(required=True)
    members = ndb.StringProperty(repeated=True)
    size = ndb.IntegerProperty(default=0, indexed=False)


class Question(ndb.Model):
    """A model to hold the question and options of each round"""
    options_total = ndb.IntegerProperty(required=True, indexed=False)
    question = ndb.StringProperty(required=True, indexed=False)
    options = ndb.StringProperty(repeated=True, indexed=False)


class Round(ndb.Model):
    """A model to hold the properties of each round"""
    deadline = ndb.StringProperty(required=True, indexed=False)
    number = ndb.IntegerProperty(required=True)
    description = ndb.StringProperty(indexed=False)
    is_quiz = ndb.BooleanProperty(default=False, indexed=False)
    quiz = ndb.StructuredProperty(Question, indexed=False)


class Response(ndb.Model):
    """A response model for all the answers"""
    option = ndb.StringProperty(default='NA', indexed=False)
    comment = ndb.StringProperty(required=True, indexed=False)
    response = ndb.StringProperty(repeated=True, indexed=False)
    summary = ndb.StringProperty(indexed=False)
    student = ndb.StringProperty(required=True)


errorCodes = {
    '100': "Oops! Something went wrong please try again.",
    '101': "Sorry you are not registered with this Application, please contact your Instructor.",
    '102': "Sorry you are not an instructor."
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
            url = users.create_login_url(self.request.uri)
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
                    logging.info(template_values)
                    self.response.write(template.render(template_values))
                else:
                    logging.info(str(result) + ' navigated to Error')
                    self.redirect('/error?code=102')
            else:
                self.redirect('/error?code=101')
                # result = Admin.query(Admin.email == user.email()).get()
                # url = users.create_logout_url(self.request.uri)
                # if result:
                #     logging.info('Admin logged in ' + str(result))
                #     section = str(result.key.parent().string_id())
                #     template_values = {
                #         'logouturl': url,
                #         'section': section
                #     }
                #     students = Student.query(ancestor=result.key).fetch()
                #     if students:
                #         template_values['students'] = students
                #     template = JINJA_ENVIRONMENT.get_template('admin.html')
                #     self.response.write(template.render(template_values))
                # else:
                #     result = Student.query(Student.email == user.email()).get()
                #     if result:
                #         logging.info('Student logged in ' + str(result))
                #         class_obj = Class.get_by_id(result.class_name)
                #         logging.info(class_obj)
                #         if class_obj.current_round > 0:
                #             current_round = Round.get_by_id(class_obj.current_round, parent=class_obj.key)
                #             if current_round:
                #                 if not current_round.is_quiz:
                #                     self.redirect('/discussion')
                #                     return
                #                 deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                #                 logging.info(deadline)
                #                 current_time = datetime.datetime.now()
                #                 logging.info(current_time)
                #                 response = Response.get_by_id(result.email, parent=current_round.key)
                #                 logging.info(str(response))
                #                 if response:
                #                     template_values = {
                #                         'url': url,
                #                         'option': response.option,
                #                         'comment': response.comment
                #                     }
                #                     if response.summary:
                #                         template_values['summary'] = response.summary
                #                 else:
                #                     template_values = {
                #                         'url': url
                #                     }
                #                 if deadline < current_time:
                #                     template_values['expired'] = True
                #                 if class_obj.current_round == 5:                        # To be changed
                #                     template_values['last_round'] = True
                #                 template_values['deadline'] = current_round.deadline
                #                 template_values['question'] = current_round.quiz.question
                #                 template_values['options'] = current_round.quiz.options
                #                 template_values['number'] = current_round.quiz.options_total
                #                 template = JINJA_ENVIRONMENT.get_template('home.html')
                #                 self.response.write(template.render(template_values))
                #             else:
                #                 self.response.write("Sorry rounds are not active. <a href='" + url + "'>Logout</a>")
                #         else:
                #             self.response.write("Sorry no rounds are active right now, please check back later. <a href='" + url + "'>Logout</a>")
                #     else:
                #         self.response.write("Sorry you are not yet registered with this application, please contact your professor. <a href='" + url + "'>Logout</a>")
        else:
            self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            student = Student.query(Student.email == user.email()).get()
            if student:
                option = self.request.get('option').lower()
                comment = self.request.get('comm')
                summary = self.request.get('summary')
                if not (option and comment):
                    self.response.write('Sorry! There was some error submitting your response please try again later.')
                else:
                    class_obj = Class.get_by_id(student.class_name)
                    current_round = Round.get_by_id(class_obj.current_round, parent=class_obj.key)
                    if current_round:
                        deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                        logging.info(deadline)
                        current_time = datetime.datetime.now()
                        logging.info(current_time)
                        if deadline >= current_time:
                            response = Response(parent=current_round.key, id=student.email)
                            response.option = option
                            response.comment = comment
                            response.student = student.email
                            if summary:
                                response.summary = summary
                            response.put()
                            # logging.info('Response saved from ' + str(student.email) + ', opt: ' + str(option) + ', comment: ' + str(comment))
                            self.response.write(
                                'Thank you, your response have been saved and you can edit your response any time before the deadline.')
                        else:
                            self.response.write(
                                'Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                    else:
                        self.response.write(
                            'Sorry! There was some error submitting your response please try again later.')
            else:
                self.response.write('Sorry! There was some error submitting your response please try again later.')
        else:
            self.response.write('Sorry! There was some error submitting your response please try again later.')


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
                    template_values = {'logouturl': url}
                    courses = Course.query(ancestor=result.key).fetch()
                    if courses:
                        course = None
                        template_values['courses'] = courses
                        course_name = self.request.get('course')
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
                            selected_section = self.request.get('section')
                            section = None
                            if selected_section:
                                selected_section = selected_section.upper()
                                section = Section.get_by_id(selected_section, parent=course.key)
                            if not section:
                                section = sections[0]
                            template_values['selectedSection'] = section.name
                            template_values['students'] = section.students
                    template = JINJA_ENVIRONMENT.get_template('students.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/home"')
            else:
                self.redirect('/home"')


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
                                if email not in section.students:
                                    section.students.append(email)
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
                                if email in section.students:
                                    section.students.remove(email)
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


def check_response(response):
    for i in range(1, len(response)):
        if response[i] not in ['support', 'neutral', 'disagree']:
            return True
    return False


class Discussion(webapp2.RequestHandler):
    """Redirecting accordingly based on email"""

    def get(self):
        user = users.get_current_user()
        if user:
            student = Student.query(Student.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if student:
                logging.info('Student redirect to discussion ' + str(student))
                class_obj = Class.get_by_id(student.class_name)
                current_page = self.request.get('round')
                if class_obj.current_round > 0:
                    if class_obj.current_round == 1:
                        self.redirect('/home')
                        return
                    display_round = class_obj.current_round
                    if class_obj.current_round == 5:  # To be changed
                        display_round = 5
                    if current_page:
                        try:
                            current_page = int(current_page) + 1
                            logging.info(current_page)
                            if current_page > 4 or current_page < 2:  # To be changed
                                raise Exception('wrong_round')
                            else:
                                display_round = current_page
                        except:
                            self.redirect('/discussion')
                            return
                    current_round = Round.get_by_id(display_round, parent=class_obj.key)
                    if current_round:
                        deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                        logging.info(deadline)
                        current_time = datetime.datetime.now()
                        logging.info(current_time)
                        try:
                            group = Group.get_by_id(student.group, parent=student.key.parent().parent())
                        except:
                            self.response.write(
                                'Sorry, your group was not found. Please contact your professor. <a href="' + url + '"">Logout</a>')
                            return
                        if group:
                            comments = []
                            for stu in group.members:
                                response = Response.get_by_id(stu, parent=Round.get_by_id(display_round - 1,
                                                                                          parent=class_obj.key).key)
                                if response:
                                    comment = {
                                        'alias': Student.get_by_id(stu, parent=student.key.parent()).alias,
                                        'response': response.comment,
                                        'opinion': response.response
                                    }
                                    # if response.option != 'NA':
                                    #     comment['option'] = Round.get_by_id(display_round - 1, parent=class_obj.key).quiz.options[int(response.option[-1]) - 1]
                                    comments.append(comment)
                            logging.info(comments)
                            template_values = {
                                'url': url,
                                'alias': student.alias,
                                'comments': comments
                            }
                            response = Response.get_by_id(student.email, parent=current_round.key)
                            if response:
                                template_values['comment'] = response.comment
                                template_values['response'] = ','.join(str(item) for item in response.response)
                            if deadline < current_time or display_round != class_obj.current_round:
                                template_values['expired'] = True
                            template_values['deadline'] = current_round.deadline
                            template_values['round'] = class_obj.current_round
                            template_values['curr_page'] = display_round
                            template_values['description'] = current_round.description
                            if class_obj.current_round == 5:  # To be changed
                                template_values['round'] = 5
                                template_values['expired'] = True
                            logging.info(template_values)
                            template = JINJA_ENVIRONMENT.get_template('discussion.html')
                            self.response.write(template.render(template_values))
                        else:
                            self.response.write(
                                'Sorry, your group was not found. Please contact your professor. <a href="' + url + '"">Logout</a>')
                    else:
                        self.response.write('Sorry rounds are not active. <a href="' + url + '"">Logout</a>')
                else:
                    self.response.write(
                        'Sorry no rounds are active right now, please check back later. <a href="' + url + '"">Logout</a>')
            else:
                self.response.write(
                    'Sorry you are not yet registered with this application, please contact your professor. <a href="' + url + '"">Logout</a>')
        else:
            self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            student = Student.query(Student.email == user.email()).get()
            if student:
                response = json.loads(self.request.get('response'))
                comment = self.request.get('comm')
                if (not (response and comment)) or check_response(response):
                    self.response.write('Sorry! There was some error submitting your response please try again later.')
                else:
                    logging.info(response)
                    class_obj = Class.get_by_id(student.class_name)
                    if class_obj.current_round == 5:  # To be changed
                        self.response.write('Sorry! you cannot submit to this round.')
                        return
                    current_round = Round.get_by_id(class_obj.current_round, parent=class_obj.key)
                    if current_round:
                        deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                        logging.info(deadline)
                        current_time = datetime.datetime.now()
                        logging.info(current_time)
                        if deadline >= current_time:
                            new_response = Response(parent=current_round.key, id=student.email)
                            new_response.comment = comment
                            new_response.student = student.email
                            for i in range(1, len(response)):
                                new_response.response.append(response[i])
                            new_response.put()
                            # logging.info('Response saved from ' + str(student.email) + ', comment: ' + str(comment))
                            self.response.write(
                                'Thank you, your response have been saved and you can edit your response any time before the deadline.')
                        else:
                            self.response.write(
                                'Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                    else:
                        self.response.write(
                            'Sorry! There was some error submitting your response please try again later.')
            else:
                self.response.write('Sorry! There was some error submitting your response please try again later.')
        else:
            self.response.write('Sorry! There was some error submitting your response please try again later.')


class Groups(webapp2.RequestHandler):
    """Handling groups page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if result:
                logging.info('Admin navigated to groups ' + str(result))
                section = str(result.key.parent().string_id())
                template_values = {}
                try:
                    response = Response.query(ancestor=Round.get_by_id(1, parent=result.key.parent()).key).fetch()
                    groups = Class.get_by_id(section).groups
                    logging.info('Groups found: ' + str(groups))
                    student = Student.query(ancestor=result.key).fetch()
                    for res in response:
                        for stu in student:
                            if res.student == stu.email:
                                res.group = stu.group
                    logging.info(response)
                    template_values = {
                        'responses': response,
                        'group': groups
                    }
                except:
                    logging.info("No rounds are available.")
                finally:
                    template_values['logouturl'] = url
                    template_values['section'] = section
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
            result = Admin.query(Admin.email == user.email()).get()
            if result:
                class_name = self.request.get('class')
                groups = int(self.request.get('group'))
                class_obj = Class.get_by_id(class_name)
                if class_obj:
                    class_obj.groups = groups
                    class_obj.put()
                    self.response.write('success')
                else:
                    self.response.write('error')
            else:
                self.response.write('error')
        else:
            self.response.write('error')


class UpdateGroups(webapp2.RequestHandler):
    """Updating groups of students"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            if result:
                groups = self.request.get('groups')
                logging.info(groups)
                groups = json.loads(groups)
                student = Student.query(ancestor=result.key).fetch()
                for stu in student:
                    if groups[stu.email]:
                        if stu.group != int(groups[stu.email]):
                            stu.group = int(groups[stu.email])
                            group = Group.get_by_id(stu.group, parent=result.key.parent())
                            if group:
                                if stu.email not in group.members:
                                    group.members.append(stu.email)
                                    group.size += 1
                                    stu.alias = 'S' + str(group.size)
                                    group.put()
                            else:
                                group = Group(parent=result.key.parent(), id=stu.group)
                                group.number = stu.group
                                group.size += 1
                                group.members = [stu.email]
                                stu.alias = 'S' + str(group.size)
                                group.put()
                            stu.put()
                self.response.write('true')
            else:
                self.response.write('error')
        else:
            self.response.write('error')


class Rounds(webapp2.RequestHandler):
    """Handling rounds page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if result:
                logging.info('Admin navigated to rounds ' + str(result))
                section = str(result.key.parent().string_id())
                class_obj = Class.get_by_id(section)
                template_values = {
                    'logouturl': url,
                    'section': section,
                    'round': class_obj.current_round
                }
                rounds = Round.query(ancestor=class_obj.key).fetch()
                if rounds:
                    template_values['rounds'] = rounds
                template = JINJA_ENVIRONMENT.get_template('rounds.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            if result:
                class_name = str(result.key.parent().string_id())
                time = self.request.get('time')
                round_val = int(self.request.get('round'))
                quiz = self.request.get('quiz')
                class_obj = Class.get_by_id(class_name)
                if class_obj:
                    class_obj.current_round = round_val
                    class_obj.rounds = round_val
                    class_obj.put()
                    round_obj = Round(parent=class_obj.key, id=round_val)
                    round_obj.deadline = time
                    round_obj.number = round_val
                    if quiz == 'T':
                        round_obj.is_quiz = True
                        question = self.request.get('question')
                        number_options = int(self.request.get('number'))
                        options = json.loads(self.request.get('options'))
                        round_obj.quiz = Question(options_total=number_options, question=question, options=options)
                    else:
                        description = self.request.get('description')
                        round_obj.description = description
                    round_obj.put()
                    logging.info(round_obj)
                    self.response.write('Success, Round ' + str(round_val) + ' is now active.')
                else:
                    self.response.write('Error, finding the given class.')
            else:
                self.response.write('Error, Admin not found.')
        else:
            self.response.write('Error, please log in to post.')


class Responses(webapp2.RequestHandler):
    """Handling responses page for admin console"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if result:
                logging.info('Admin navigated to responses ' + str(result))
                section = str(result.key.parent().string_id())
                class_obj = Class.get_by_id(section)
                template_values = {
                    'logouturl': url,
                    'section': section,
                    'round': class_obj.rounds
                }
                resp = {}
                for i in range(1, class_obj.rounds + 1):
                    response = Response.query(ancestor=Round.get_by_id(i, parent=result.key.parent()).key).fetch()
                    # response is a list of all the responses for the round i
                    if response:
                        resp[str(i)] = response
                template_values['responses'] = resp
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
            result = Admin.query(Admin.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if result:
                logging.info('Admin navigated to groups_responses ' + str(result))
                section = str(result.key.parent().string_id())
                class_obj = Class.get_by_id(section)
                template_values = {
                    'logouturl': url,
                    'section': section,
                    'round': class_obj.rounds,
                    'groups': class_obj.groups
                }
                resp = {}
                for g in range(1, class_obj.groups + 1):
                    for r in range(1, class_obj.rounds + 1):
                        resp['group_' + str(g) + '_' + str(r)] = []
                for r in range(1, class_obj.rounds + 1):
                    response = Response.query(ancestor=Round.get_by_id(r, parent=result.key.parent()).key).fetch()
                    if response:
                        for res in response:
                            stu = Student.query(Student.email == res.student).get()
                            res.alias = stu.alias
                            resp['group_' + str(stu.group) + '_' + str(r)].append(res)
                template_values['responses'] = resp
                logging.info('Resp' + str(template_values))
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
    ('/discussion', Discussion),
    ('/responses', Responses),
    ('/group_responses', GroupResponses),
    ('/addStudent', AddStudent),
    ('/removeStudent', RemoveStudent),
    ('/groups', Groups),
    ('/rounds', Rounds),
    ('/addGroups', AddGroups),
    ('/updateGroups', UpdateGroups)
], debug=True)
