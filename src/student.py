import datetime
import json
import logging

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

import consider
import model
import utils


class StudentsPage(webapp2.RequestHandler):
    """Page for instructor to add students to a particular section"""

    def get(self):
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is model.Instructor:
                    logging.info('Instructor navigated to Students ' + str(result))
                    course_name = self.request.get('course')
                    selected_section = self.request.get('section')
                    template_values = utils.get_courses_and_sections(result, course_name, selected_section)
                    template_values['logouturl'] = url
                    template = consider.JINJA_ENVIRONMENT.get_template('students.html')
                    self.response.write(template.render(template_values))
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class SubmitResponse(webapp2.RequestHandler):
    """Accept responses from students and save them in the database"""

    def post(self):
        user = users.get_current_user()
        if user:
            student = utils.get_role(user)
            if student and type(student) is model.Student:
                option = self.request.get('option').lower()
                comment = self.request.get('comm')
                summary = self.request.get('summary')
                res = self.request.get('response')
                section_key = self.request.get('section')
                if section_key:
                    try:
                        section = ndb.Key(urlsafe=section_key).get()
                        if section:
                            current_round = model.Round.get_by_id(section.current_round, parent=section.key)
                            if current_round:
                                response = model.Response(parent=current_round.key, id=student.email)
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
                                    if not (res and comment) or utils.check_response(res):
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
                                    self.response.write(
                                            'Thank you, your response have been saved and you can edit your response any time before the deadline.')
                                else:
                                    self.response.write(
                                            'Sorry, the time for submission for this round has expired and your response was not saved, please wait for the next round.')
                            else:
                                self.response.write('Sorry! The round is not visible, please try again later.')
                        else:
                            self.response.write('Sorry! The section is not visible, please try again later.')
                    except:
                        self.response.write(
                                'Sorry! There was some error submitting your response please try again later.')
                else:
                    self.response.write('Invalid Parameters!')
            else:
                self.response.write('Sorry! You were not identified as a student, please try again later.')
        else:
            self.response.write('Sorry! User is not recognized, please try again later.')
