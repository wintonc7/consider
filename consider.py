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


class Class(ndb.Model):
    """A main model for a particular class and root of the application"""
    name = ndb.StringProperty(required="True")
    groups = ndb.IntegerProperty(default=0, indexed=False)
    current_round = ndb.IntegerProperty(default=0, indexed=False)
    rounds = ndb.IntegerProperty(default=0, indexed=False)


class Admin(ndb.Model):
    """A main model for representing admins"""
    email = ndb.StringProperty(required=True)


class Student(ndb.Model):
    """A student model for all the students"""
    email = ndb.StringProperty(required=True)
    alias = ndb.StringProperty(default='NA')
    class_name = ndb.StringProperty(required=True)
    group = ndb.IntegerProperty(default=0, indexed=False)


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
    is_quiz = ndb.BooleanProperty(default=False, indexed=False)
    quiz = ndb.StructuredProperty(Question, indexed=False)


class Response(ndb.Model):
    """A response model for all the answers"""
    option = ndb.StringProperty(default='NA', indexed=False)
    comment = ndb.StringProperty(required=True, indexed=False)
    response = ndb.StringProperty(repeated=True, indexed=False)
    summary = ndb.StringProperty(indexed=False)
    student = ndb.StringProperty(required=True)


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
            result = Admin.query(Admin.email == user.email()).get()
            url = users.create_logout_url(self.request.uri)
            if result:
                logging.info('Admin logged in ' + str(result))
                section = str(result.key.parent().string_id())
                template_values = {
                    'logouturl': url,
                    'section': section
                }
                students = Student.query(ancestor=result.key).fetch()
                if students:
                    template_values['students'] = students
                template = JINJA_ENVIRONMENT.get_template('admin.html')
                self.response.write(template.render(template_values))
            else:
                result = Student.query(Student.email == user.email()).get()
                if result:
                    logging.info('Student logged in ' + str(result))
                    class_obj = Class.get_by_id(result.class_name)
                    logging.info(class_obj)
                    if class_obj.current_round > 0:
                        current_round = Round.get_by_id(class_obj.current_round, parent=class_obj.key)
                        if current_round:
                            if not current_round.is_quiz:
                                self.redirect('/discussion')
                                return
                            deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                            logging.info(deadline)
                            current_time = datetime.datetime.now()
                            logging.info(current_time)
                            response = Response.get_by_id(result.email, parent=current_round.key)
                            logging.info(str(response))
                            if response:
                                template_values = {
                                    'url': url,
                                    'option': response.option,
                                    'comment': response.comment
                                }
                            else:
                                template_values = {
                                    'url': url
                                }
                            if deadline < current_time:
                                template_values['expired'] = True
                            if class_obj.current_round == 4:                        # To be changed
                                template_values['last_round'] = True
                            if response.summary:
                                template_values['summary'] = response.summary
                            template_values['deadline'] = current_round.deadline
                            template_values['question'] = current_round.quiz.question
                            template_values['options'] = current_round.quiz.options
                            template_values['number'] = current_round.quiz.options_total
                            template = JINJA_ENVIRONMENT.get_template('home.html')
                            self.response.write(template.render(template_values))
                        else:
                            self.response.write("Sorry rounds are not active. <a href='" + url + "'>Logout</a>")
                    else:
                        self.response.write("Sorry no rounds are active right now, please check back later. <a href='" + url + "'>Logout</a>")
                else:
                    self.response.write("Sorry you are not yet registered with this application, please contact your professor. <a href='" + url + "'>Logout</a>")
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
                            logging.info('Response saved from ' + str(student.email) + ', opt: ' + str(option) + ', comment: ' + str(comment))
                            self.response.write('Thank you, your response have been saved and you can edit your response any time before the deadline.')
                        else:
                            self.response.write('Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                    else:
                        self.response.write('Sorry! There was some error submitting your response please try again later.')
            else:
                self.response.write('Sorry! There was some error submitting your response please try again later.')
        else:
            self.response.write('Sorry! There was some error submitting your response please try again later.')


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
                    if class_obj.current_round == 4:        # To be changed
                        display_round = 3
                    if current_page:
                        try:
                            current_page = int(current_page) + 1
                            logging.info(current_page)
                            if current_page > 3 or current_page < 2:    # To be changed
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
                            self.response.write('Sorry, your group was not found. Please contact your professor. <a href="' + url + '"">Logout</a>')
                            return
                        if group:
                            comments = []
                            for stu in group.members:
                                response = Response.get_by_id(stu, parent=Round.get_by_id(display_round - 1, parent=class_obj.key).key)
                                if response:
                                    comment = {
                                        'alias': Student.get_by_id(stu, parent=student.key.parent()).alias,
                                        'response': response.comment
                                    }
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
                            if class_obj.current_round == 4:        # To be changed
                                template_values['round'] = 3
                            logging.info(template_values)
                            template = JINJA_ENVIRONMENT.get_template('discussion.html')
                            self.response.write(template.render(template_values))
                        else:
                            self.response.write('Sorry, your group was not found. Please contact your professor. <a href="' + url + '"">Logout</a>')
                    else:
                        self.response.write('Sorry rounds are not active. <a href="' + url + '"">Logout</a>')
                else:
                    self.response.write('Sorry no rounds are active right now, please check back later. <a href="' + url + '"">Logout</a>')
            else:
                self.response.write('Sorry you are not yet registered with this application, please contact your professor. <a href="' + url + '"">Logout</a>')
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
                            logging.info('Response saved from ' + str(student.email) + ', comment: ' + str(comment))
                            self.response.write('Thank you, your response have been saved and you can edit your response any time before the deadline.')
                        else:
                            self.response.write('Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                    else:
                        self.response.write('Sorry! There was some error submitting your response please try again later.')
            else:
                self.response.write('Sorry! There was some error submitting your response please try again later.')
        else:
            self.response.write('Sorry! There was some error submitting your response please try again later.')


class AddStudent(webapp2.RequestHandler):
    """Adding students to the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            result = Admin.query(Admin.email == user.email()).get()
            if result:
                class_name = self.request.get('class')
                emails = json.loads(self.request.get('emails'))
                if emails:
                    for email in emails:
                        student = Student(parent=result.key, id=email)
                        student.email = email
                        student.class_name = class_name
                        student.put()
                    self.response.write(len(emails))
                else:
                    self.response.write("Error! invalid arguments.")
            else:
                self.response.write('Error! unauthorized user.')
        else:
            self.response.write('Error! Please log in.')


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
                    round_obj.put()
                    logging.info(round_obj)
                    self.response.write('Success, Round ' + str(round_val) + ' is now active.')
                else:
                    self.response.write('Error, finding the given class.')
            else:
                self.response.write('Error, Admin not found.')
        else:
            self.response.write('Error, please log in to post.')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home', HomePage),
    ('/discussion', Discussion),
    ('/addStudent', AddStudent),
    ('/groups', Groups),
    ('/rounds', Rounds),
    ('/addGroups', AddGroups),
    ('/updateGroups', UpdateGroups)
], debug=True)