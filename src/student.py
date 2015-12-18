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

import model
import utils


class SubmitResponse(webapp2.RequestHandler):
    """
    API to submit a student's response to the current round.

    The student can save the response and return again, before the deadline, to modify it.
    """

    def post(self):
        """
        HTTP POST method to submit the response.
        """
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


class SectionPage(webapp2.RequestHandler):
    """
    API to redirect a student based on what stage she is in in a particular section:
    lead-in question, discussion or summary round.

    If no round is active for this section, it redirects to an appropriate error page.
    """
    def get(self):
        """
        HTTP GET method to retrieve the sections and rounds under it.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is model.Student:
                    logging.info('Student logged in ' + str(result))
                    section_key = self.request.get('section')
                    if section_key:
                        try:
                            section = ndb.Key(urlsafe=section_key).get()
                            if section:
                                if section.current_round == 0:
                                    self.redirect('/error?code=103')
                                else:
                                    curr_round = model.Round.get_by_id(section.current_round, parent=section.key)
                                    if curr_round:
                                        if not curr_round.is_quiz:
                                            self.redirect('/discussion?section=' + section_key)
                                            return
                                        deadline = datetime.datetime.strptime(curr_round.deadline, '%Y-%m-%dT%H:%M')
                                        current_time = datetime.datetime.now()
                                        template_values = {
                                            'url': url
                                        }
                                        response = model.Response.get_by_id(result.email, parent=curr_round.key)
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
                                        template = utils.JINJA_ENVIRONMENT.get_template('home.html')
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


class Discussion(webapp2.RequestHandler):
    """
    API to retrieve discussion information, i.e. the responses from previous round and deadline for the current round.
    """
    def get(self):
        """
        HTTP GET method to retrieve the discussion information.
        """
        user = users.get_current_user()
        if user:
            result = utils.get_role(user)
            if result:
                # User is either Instructor or Student
                url = users.create_logout_url(self.request.uri)
                if type(result) is model.Student:
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
                                    d_round = model.Round.get_by_id(requested_round, parent=section.key)
                                    if d_round:
                                        group = 0
                                        alias = None
                                        for stu in section.students:
                                            if stu.email == result.email:
                                                group = stu.group
                                                alias = stu.alias
                                                break
                                        if group != 0 and alias:
                                            group = model.Group.get_by_id(group, parent=section.key)
                                            if group:
                                                comments = []
                                                previous_round = model.Round.get_by_id(requested_round - 1,
                                                                                       parent=section.key)
                                                for stu in group.members:
                                                    response = model.Response.get_by_id(stu, parent=previous_round.key)
                                                    if response:
                                                        for s in section.students:
                                                            if s.email == stu:
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
                                                    'url': url,
                                                    'alias': alias,
                                                    'comments': comments
                                                }
                                                stu_response = model.Response.get_by_id(result.email,
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
                                                template = utils.JINJA_ENVIRONMENT.get_template('discussion.html')
                                                self.response.write(template.render(template_values))
                                            else:
                                                logging.error(
                                                        "Group not found for " + str(result) + " Section: " + str(
                                                                section))
                                                self.redirect('/error?code=105')
                                        else:
                                            logging.error(
                                                    "Group not found for " + str(result) + " Section: " + str(section))
                                            self.redirect('/error?code=105')
                                    else:
                                        logging.info(
                                                "Requested round not found for " + str(result) + " Section: " + str(
                                                        section))
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
