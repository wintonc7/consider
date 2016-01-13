"""
student.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Student role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Dec. 18, 2015

--------------------


"""

import datetime
import json
import logging

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
        """
        HTTP GET method to retrieve the sections and rounds under it.
        """
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            logouturl = users.create_logout_url(self.request.uri)
            logging.info('Student logged in ' + str(student))
            section_key = self.request.get('section')
            if section_key:
                try:
                    section = ndb.Key(urlsafe=section_key).get()
                    if section:
                        if section.current_round == 0:
                            self.redirect('/error?code=103')
                        else:
                            curr_round = models.Round.get_by_id(section.current_round, parent=section.key)
                            if curr_round:
                                if not curr_round.is_quiz:
                                    self.redirect('/discussion?section=' + section_key)
                                    return
                                deadline = datetime.datetime.strptime(curr_round.deadline, '%Y-%m-%dT%H:%M')
                                current_time = datetime.datetime.now()
                                template_values = {
                                    'logouturl': logouturl
                                }
                                response = models.Response.get_by_id(student.email, parent=curr_round.key)
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
                                template = utils.jinja_env().get_template('student_round.html')
                                self.response.write(template.render(template_values))
                            else:
                                self.redirect('/error?code=104')
                    else:
                        self.redirect('/home')
                except Exception as e:
                    logging.error('Got exception: ' + e.message)
                    self.redirect('/home')
            else:
                self.redirect('/')
        else:
            self.redirect('/')

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
                                    self.response.write('Invalid Parameters!')
                                    return
                                if current_round.number != 1 and not summary:
                                    self.response.write('Invalid Parameters!')
                                    return
                                response.option = option
                                response.summary = summary if summary else ''
                            else:
                                res = json.loads(res)
                                if not (res and comment) or not utils.is_valid_response(res):
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
                        utils.error('Sorry! The section is not visible, please try again later.', handler=self)
                except:
                    utils.error(
                            'Sorry! There was some error submitting your response please try again later.',
                            handler=self)
            else:
                utils.error('Invalid Parameters!', handler=self)
        else:
            utils.error('Sorry! User is not recognized, please try again later.', handler=self)


class Discussion(webapp2.RequestHandler):  # FIXME Aliases mixed up.
    """
    API to retrieve discussion information, i.e. the responses from previous round and deadline for the current round.
    """

    def get(self):
        """
        HTTP GET method to retrieve the discussion information.
        """
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            logout_url = users.create_logout_url(self.request.uri)
            utils.log('Student navigated to discussion ' + str(student))
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
                            requested_round = int(requested_round) if requested_round else section.current_round
                            d_round = models.Round.get_by_id(requested_round, parent=section.key)
                            if d_round:
                                group = 0
                                alias = None
                                for _student in section.students:
                                    if _student.email == student.email:
                                        group = _student.group
                                        alias = _student.alias
                                        break
                                if group != 0 and alias:
                                    group = models.Group.get_by_id(group, parent=section.key)
                                    if group:
                                        comments = []
                                        previous_round = models.Round.get_by_id(requested_round - 1,
                                                                                parent=section.key)
                                        for _student in group.members:
                                            response = models.Response.get_by_id(_student, parent=previous_round.key)
                                            if response:
                                                for s in section.students:
                                                    if s.email == _student:
                                                        comment = {
                                                            'alias': s.alias,
                                                            'response': response.comment,
                                                            'opinion': response.response
                                                        }
                                                        if response.option != 'NA':
                                                            comment['option'] = previous_round.quiz.options[
                                                                int(response.option[-1]) - 1]
                                                        comments.append(comment)
                                                        break
                                        template_values = {
                                            'logouturl': logout_url,
                                            'alias': alias,
                                            'comments': comments
                                        }
                                        stu_response = models.Response.get_by_id(student.email,
                                                                                 parent=d_round.key)
                                        if stu_response:
                                            template_values['comment'] = stu_response.comment
                                            template_values['response'] = ','.join(
                                                    str(item) for item in stu_response.response)
                                        deadline = datetime.datetime.strptime(d_round.deadline,
                                                                              '%Y-%m-%dT%H:%M')
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
                                        template = utils.jinja_env().get_template('student_discussion.html')
                                        self.response.write(template.render(template_values))
                                    else:
                                        utils.error(
                                                'Group not found for {0} Section: {1}'.format(str(student), str(
                                                        section)))
                                        self.redirect('/error?code=105')
                                else:
                                    utils.error(
                                            'Group not found for {0} Section: {1}'.format(str(student), str(section)))
                                    self.redirect('/error?code=105')
                            else:
                                utils.log(
                                        'Requested round not found for {0} Section: {1}'.format(str(student), str(
                                                section)))
                                self.redirect('/home')
                    else:
                        utils.log('Section not found for key: ' + section_key)
                        self.redirect('/home')
                except Exception as e:
                    utils.log('Found exception ' + e.message)
                    self.redirect('/home')
            else:
                self.redirect('/home')
        else:
            self.redirect('/')


class HomePage(webapp2.RequestHandler):
    def get(self):
        """
        Display a list of active ``Section``_\ s this ``Student``_ is enrolled in.
        """
        role, student = utils.get_role_user()
        if student and role == models.Role.student:
            logouturl = users.create_logout_url(self.request.uri)
            template_values = {'logouturl': logouturl, 'nickname': student.email}
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
            utils.error('user is empty or not student')
