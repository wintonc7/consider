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
        # First, grab the information for the currently logged in user
        role, student = utils.get_role_user()
        # And check that they're a student
        if not student or role != models.Role.student:
            # Redirect home if not a student
            self.redirect('/home')
        else:
            # Otherwise, log which student made the get
            utils.log('Student logged in: ' + str(student))
            # And grab the key for the section
            section_key = self.request.get('section')
            # Make sure that it isn't null
            if not section_key:
                # Error if so, and redirect home
                utils.error('Section_key is null')
                self.redirect('/home')
            else:
                # And then grab the section from the key
                section = ndb.Key(urlsafe=section_key).get()
                # Making sure it's not null
                if not section:
                    # Error if so
                    utils.error('Section is null')
                else:
                    # Now check if the current round is 0
                    if section.current_round == 0:
                        # And redirect to an error if so
                        self.redirect('/error?code=103')
                    else:
                        # Otherwise, we need to set our template values
                        # Send the current section and round number
                        current_round = self.request.get('round')
                        self.render_template(student, section, current_round)
                    #end
                #end
            #end
        #end
    #end get

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

    def render_template(self, student, section, round_number):
        # Now check that the round number passed in actually exists, and set
        # the requested round number appropriately if not
        if round_number:
            requested_round_number = int(round_number)
        else:
            requested_round_number = section.current_round
        #end

        # Grab the requested round
        requested_round = models.Round.get_by_id(requested_round_number, parent=section.key)
        # And check that it's not null, redirect to error if so
        if not requested_round: self.redirect('/error?code=104')
        else:
            # Otherwise we need to set up our template values, create empty dict
            template_values = {}
            # Grab the deadline from the requested round
            deadline = datetime.datetime.strptime(requested_round.deadline, '%Y-%m-%dT%H:%M')
            # And the current time
            current_time = datetime.datetime.now()
            # And check if we're dealing with an expired round
            if deadline < current_time or requested_round_number < section.current_round:
                # Set the template value if so
                template_values['expired'] = True
            #end
            # Check if we're on the last round
            if requested_round.is_quiz and requested_round_number > 1:
                template_values['last_round'] = True
            #end
            # Now, just grab all the other generic values we need directly
            template_values['deadline'] = requested_round.deadline
            template_values['sectionKey'] = self.request.get('section')
            template_values['rounds'] = section.current_round
            template_values['show_name'] = not requested_round.is_anonymous
            logout_url = users.create_logout_url(self.request.uri)
            template_values['logouturl'] = logout_url
            template_values['curr_page'] = requested_round_number

            # Now we need to check if it's the lead-in or summary question
            if requested_round.is_quiz:
                # And set template values for quiz round
                self.quiz_view_template(student, requested_round, template_values)
                # And set the right template
                template = utils.jinja_env().get_template('student_round.html')
            else:
                # Otherwise, set up template values for discussion round
                self.discussion_view_template(student, section, requested_round_number, template_values)
                # And set the right template
                template = utils.jinja_env().get_template('student_discussion.html')
            #end
            # Now, render it.
            self.response.write(template.render(template_values))
        #end
    #end render_templates

    def quiz_view_template(self, student, rround, template_values):
        # Grab the response for this round by this student
        response = models.Response.get_by_id(student.email, parent=rround.key)
        # And if the question has been previously answered
        if response:
            # Set template values for what the student previously said
            template_values['option'] = response.option
            template_values['comment'] = response.comment
            template_values['summary'] = response.summary
        #end
        # Now set the remaining template values directly
        template_values['question'] = rround.quiz.question
        template_values['options'] = rround.quiz.options
        template_values['number'] = rround.quiz.options_total
    #end quiz_view_template

    def discussion_view_template(self, student, section, round_number, template_values):
        # Init group and alias to "null" values
        group = 0
        alias = None
        # Loop over all the students in the section
        for _student in section.students:
            # And find the email that matches the current student
            if _student.email == student.email:
                # And grab the group and alias from there
                group = _student.group
                template_values['alias'] = _student.alias
                break
            #end
        #end
        # Double check that the student was found in this section
        if group > 0 and template_values['alias']:
            # Now grab the actual group from the db
            group = models.Group.get_by_id(group, parent=section.key)
            # Double check that it was found
            if group:
                # Depending on round number, we have to grab from 
                if round_number == 1:
                    previous_round = models.Round.get_by_id(1, parent=section.key)
                else:
                    previous_round = models.Round.get_by_id(round_number - 1, parent=section.key)
                #end
                # Now grab all the group comments for the previous round
                comments = group_comments(group, previous_round, template_values)


                # Set the template value for all the group comments
                template_values['comments'] = comments
                # And grab the logged in student's response
                stu_response = models.Response.get_by_id(student.email, parent=requested_round.key)
                # Check that they actually answered
                if stu_response:
                    # And set template values to show their previous response
                    template_values['comment'] = stu_response.comment
                    template_values['response'] = ','.join(str(item) for item in stu_response.response)
                #end
            #end
        #end
    #end discussion_view_template

    def group_comments(self, group, previous_round):
        # Init an empty list for holding the comments
        comments = []
        # Now loop over the members in the group
        for _student in group.members:
            # Grab each response from the previous round
            response = models.Response.get_by_id(_student, parent=previous_round.key)
            # Check that that student actually answered the previous
            if response:
                # Loop over the students in the section
                for s in section.students:
                    # And look for the current group member
                    if s.email == _student:
                        # Grab their alias, email, comment, and response
                        comment = {'alias': s.alias,
                                   'email': s.email,
                                   'response': response.comment,
                                   'opinion': response.response
                                   }
                        # If the response has an associated option
                        if response.option != 'NA':
                            # Grab the option
                            opt = int(response.option[-1]) - 1
                            comment['option'] = previous_round.quiz.options[opt]
                        #end
                        # And finally add the comment to the list
                        comments.append(comment)
                        break
                    #end
                #end
            #end
        #end
        return comments
    #end group_comments

#end class Rounds


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
        #end
    #end get

#end class HomePage
