"""
student.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Student role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Jan. 13, 2016

--------------------


"""

import datetime
import json

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

import models
import utils


class Rounds(webapp2.RequestHandler):
    """
    API to redirect a student based on what stage she is in in a particular section:
    lead-in question, discussion or summary round.

    If no round is active for this section, it redirects to an appropriate error page.
    """

    def get(self):
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            utils.log('Student logged in: ' + str(student))
            section_key = self.request.get('section')
            if section_key:
                section = ndb.Key(urlsafe=section_key).get()
                if section:
                    if section.current_round == 0:
                        self.redirect('/error?code=103')
                    else:
                        requested_round_number = self.request.get('round')
                        requested_round_number = int(
                            requested_round_number) if requested_round_number else section.current_round
                        requested_round = models.Round.get_by_id(requested_round_number, parent=section.key)
                        if requested_round:
                            template_values = {}
                            deadline = datetime.datetime.strptime(requested_round.deadline, '%Y-%m-%dT%H:%M')
                            current_time = datetime.datetime.now()
                            template_values['expired'] = (deadline < current_time) \
                                                         or (requested_round_number < section.current_round)
                            template_values['deadline'] = requested_round.deadline
                            template_values['sectionKey'] = section_key
                            template_values['rounds'] = section.current_round
                            template_values['show_name'] = not requested_round.is_anonymous
                            logout_url = users.create_logout_url(self.request.uri)
                            template_values['logouturl'] = logout_url
                            template_values['last_round'] = requested_round.is_quiz and requested_round_number > 1
                            template_values['curr_page'] = requested_round_number

                            if requested_round.is_quiz:
                                response = models.Response.get_by_id(student.email, parent=requested_round.key)
                                if response:
                                    template_values['option'] = response.option
                                    template_values['comment'] = response.comment
                                    template_values['summary'] = response.summary
                                template_values['question'] = requested_round.quiz.question
                                template_values['options'] = requested_round.quiz.options
                                template_values['number'] = requested_round.quiz.options_total
                                template = utils.jinja_env().get_template('student_round.html')
                                self.response.write(template.render(template_values))
                            else:
                                group = 0
                                alias = None
                                for _student in section.students:
                                    if _student.email == student.email:
                                        group = _student.group
                                        alias = _student.alias
                                        break
                                if group > 0 and alias:
                                    group = models.Group.get_by_id(group, parent=section.key)
                                    if group:
                                        comments = []
                                        if requested_round_number == 1:
                                            previous_round = models.Round.get_by_id(1, parent=section.key)
                                        else:
                                            previous_round = models.Round.get_by_id(requested_round_number - 1,
                                                                                    parent=section.key)
                                        for _student in group.members:
                                            response = models.Response.get_by_id(_student, parent=previous_round.key)
                                            if response:
                                                for s in section.students:
                                                    if s.email == _student:
                                                        comment = {'alias': s.alias,
                                                                   'email': s.email,
                                                                   'response': response.comment,
                                                                   'opinion': response.response
                                                                   }
                                                        if response.option != 'NA':
                                                            comment['option'] = previous_round.quiz.options[
                                                                int(response.option[-1]) - 1]
                                                        comments.append(comment)
                                                        break
                                        template_values['alias'] = alias
                                        template_values['comments'] = comments
                                        stu_response = models.Response.get_by_id(student.email,
                                                                                 parent=requested_round.key)
                                        if stu_response:
                                            template_values['comment'] = stu_response.comment
                                            template_values['response'] = ','.join(
                                                str(item) for item in stu_response.response)

                                template = utils.jinja_env().get_template('student_discussion.html')
                                self.response.write(template.render(template_values))
                        else:
                            self.redirect('/error?code=104')
                else:
                    utils.error('Section is null')
            else:
                utils.error('Section_key is null')
                self.redirect('/home')
        else:
            self.redirect('/home')

    def post(self):
        """
        HTTP POST method to submit the response.
        """
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            option = self.request.get('option').lower()
            comment = self.request.get('comm')
            summary = self.request.get('summary')
            res = self.request.get('response')
            section_key = self.request.get('section')
            if section_key:
                try:
                    section = ndb.Key(urlsafe=section_key).get()
                    if section:
                        current_round = models.Round.get_by_id(section.current_round, parent=section.key)
                        if current_round:
                            response = models.Response(parent=current_round.key, id=student.email)
                            if current_round.is_quiz:
                                if not (option and comment):
                                    utils.error('Invalid Parameters: option or comment is null', handler=self)
                                    return
                                # if current_round.number != 1 and not summary:
                                #     utils.error('Invalid Parameters: round is 1 or summary is null', handler=self)
                                #     return
                                response.option = option
                                response.summary = summary if summary else ''
                            else:
                                res = json.loads(res)
                                if not (res and comment) or not utils.is_valid_response(res):
                                    utils.error('Invalid Parameters: comment is null or res is not a valid response',
                                                handler=self)
                                    return
                                for i in range(1, len(res)):
                                    response.response.append(res[i])
                            deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
                            current_time = datetime.datetime.now()
                            if deadline >= current_time:
                                response.comment = comment
                                response.student = student.email
                                response.put()
                                utils.log(
                                    'Your response have been saved. You can edit it any time before the deadline.',
                                    type='S', handler=self)
                            else:
                                utils.error(
                                    'Sorry, the time for submission for this round has expired \
                                       and your response was not saved, please wait for the next round.',
                                    handler=self)
                        else:
                            utils.error('Sorry! The round is not visible, please try again later.', handler=self)
                    else:
                        utils.error('Section is null', handler=self)
                except:
                    utils.error(
                        'Sorry! There was some error submitting your response please try again later.',
                        handler=self)
            else:
                utils.error('Invalid Parameters: section_key is null', handler=self)
        else:
            utils.error('user is null or not student', handler=self)
            self.redirect('/')


class HomePage(webapp2.RequestHandler):
    def get(self):
        """
        Display a list of active ``Section``_\ s this ``Student``_ is enrolled in.
        """
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            logout_url = users.create_logout_url(self.request.uri)
            template_values = {'logouturl': logout_url, 'nickname': student.email}
            sections = student.sections
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
            template = utils.jinja_env().get_template('student_home.html')
            self.response.write(template.render(template_values))
        else:
            utils.error('user is null or not student', handler=self)
            self.redirect('/')
