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
        # First, check that the logged in user is a student
        student = utils.check_privilege(models.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/home')
        # end

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
                    self.render_template(student, section)
                    # end
                    # end
                    # end

    # end get

    def post(self):
        """
        HTTP POST method to submit the response.
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(models.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/home')
        # end

        # First, grab the section key from the page
        section_key = self.request.get('section')
        # Double check that we actually got a section key
        if not section_key:
            # Error if not
            utils.error('Invalid Parameters: section_key is null', handler=self)
        else:
            try:
                # Grab the section from the database
                section = ndb.Key(urlsafe=section_key).get()
                # And double check that it's valid
                if not section:
                    # Error if not
                    utils.error('Section is null', handler=self)
                else:
                    # Grab the current round from the database
                    current_round = models.Round.get_by_id(section.current_round, parent=section.key)
                    # And double check that it's valid
                    if not current_round:
                        # Error if not
                        utils.error('Sorry! The round is not visible, please try again later.', handler=self)
                    else:
                        self.save_submission(student, current_round)
                        # end
                        # end
            except:
                utils.error('Sorry! There was some error submitting your response please try again later.',
                            handler=self)
                # end
                # end
                # end

    # end post

    def render_template(self, student, section):
        # First, get the round number from the page
        current_round = self.request.get('round')
        # Now check that the round number passed in actually exists, and set
        # the requested round number appropriately if not
        if current_round:
            requested_round_number = int(current_round)
        else:
            requested_round_number = section.current_round
        # end

        # Grab the requested round
        requested_round = models.Round.get_by_id(requested_round_number, parent=section.key)
        # And check that it's not null
        if not requested_round:
            # Error if so
            self.redirect('/error?code=104')
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
            # end
            # Check if we're on the last round
            if requested_round.is_quiz and requested_round_number > 1:
                template_values['last_round'] = True
            # end
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
                template = utils.jinja_env().get_template('students/round.html')
            else:
                # Otherwise, set up template values for discussion round
                self.discussion_view_template(student, section, requested_round_number, template_values)
                # And set the right template
                template = utils.jinja_env().get_template('students/discussion.html')
            # end
            # Now, render it.
            self.response.write(template.render(template_values))
            # end

    # end render_templates

    def quiz_view_template(self, student, rround, template_values):
        # Grab the response for this round by this student
        response = models.Response.get_by_id(student.email, parent=rround.key)
        # And if the question has been previously answered
        if response:
            # Set template values for what the student previously said
            template_values['option'] = response.option
            template_values['comment'] = response.comment
            template_values['summary'] = response.summary
        # end
        # Now set the remaining template values directly
        template_values['question'] = rround.quiz.question
        template_values['options'] = rround.quiz.options
        template_values['number'] = rround.quiz.options_total

    # end quiz_view_template

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
                # end
        # end
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
                # end
                # Now grab all the group comments for the previous round
                comments = self.group_comments(group, section, previous_round)
                # Set the template value for all the group comments
                template_values['comments'] = comments
                # Grab the requested round
                requested_round = models.Round.get_by_id(round_number, parent=section.key)
                # Grab the discussion description
                template_values['description'] = requested_round.description
                # And grab the logged in student's response
                stu_response = models.Response.get_by_id(student.email, parent=requested_round.key)
                # Check that they actually answered
                if stu_response:
                    # And set template values to show their previous response
                    template_values['comment'] = stu_response.comment
                    utils.log("{0}".format(str(stu_response.comment)))
                    template_values['response'] = ','.join(str(item) for item in stu_response.response)
                    # end
                    # end
                    # end

    # end discussion_view_template

    def group_comments(self, group, section, previous_round):
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
                        if not response.option:
                            comment['option'] = ''
                        elif response.option != 'NA':
                            # Grab the option
                            opt = int(response.option[-1]) - 1
                            comment['option'] = previous_round.quiz.options[opt]
                        # end
                        # And finally add the comment to the list
                        comments.append(comment)
                        break
                        # end
                        # end
                        # end
        # end
        return comments

    # end group_comments

    def save_submission(self, student, current_round):
        # Create a new response object
        response = models.Response(parent=current_round.key, id=student.email)
        # Start by grabbing data from the page
        option = self.request.get('option').lower()
        comment = self.request.get('comm')
        summary = self.request.get('summary')
        res = self.request.get('response')
        # Now check whether we're on a lead-in or summary or discussion round
        if current_round.is_quiz:
            # If it is, double check that they selected an answer and commented
            if current_round.quiz.options_total > 0 and not (option and comment):
                # Error if not
                utils.error('Invalid Parameters: option or comment is null', handler=self)
                return
            # end
            # if current_round.number != 1 and not summary:
            #     utils.error('Invalid Parameters: round is 1 or summary is null', handler=self)
            #     return
            # And set the values in the response object
            response.option = option
            response.summary = summary if summary else ''
        else:
            # If a discussion question, grab the array of agree/disagree/neutral
            res = json.loads(res)
            # And double check that we have a comment and valid response
            if not (res and comment) or not utils.is_valid_response(res):
                # Error if not
                utils.error('Invalid Parameters: comment is null or res is not a valid response', handler=self)
                return
            # end
            # Now loop over the agree, etc. responses
            for i in range(1, len(res)):
                # And save them in our response object for the db
                response.response.append(res[i])
                # end
        # end
        # Grab the deadline and the current time
        deadline = datetime.datetime.strptime(current_round.deadline, '%Y-%m-%dT%H:%M')
        current_time = datetime.datetime.now()
        # And double check that they've submitted before the deadline ended
        if deadline >= current_time:
            # Set the comment and email, and save in the database
            response.comment = comment
            response.student = student.email
            response.put()
            utils.log(
                'Your response has been saved. You can edit it any time before the deadline.',
                type='Success!', handler=self)
        else:
            # Otherwise alert them that time has passed to submit for this round
            utils.error(
                'Sorry, the time for submission for this round has expired \
                   and your response was not saved, please wait for the next round.',
                handler=self)
            # end
            # end save_submission


# end class Rounds


class HomePage(webapp2.RequestHandler):
    def get(self):
        """
        Display a list of active ``Section``_\ s this ``Student``_ is enrolled in.
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(models.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/')
        # end

        # Create a url for the user to logout
        logout_url = users.create_logout_url(self.request.uri)
        # Set up the template
        template_values = {'logouturl': logout_url, 'nickname': student.email}
        # Grab the sections the student is a part of
        sections = student.sections
        # Create a new list for holding the section objects from the db
        section_list = []
        # Double check that the student is actually enrolled in a section
        if sections:
            # Loop over all the sections they're in
            for section in sections:
                # Grab it from the db
                section_obj = section.get()
                # Get the parent course for the section
                course_obj = section.parent().get()
                # Double check that both exist
                if section_obj and course_obj:
                    # Grab the section key, section name, and course name
                    sec = {
                        'key': section.urlsafe(),
                        'name': section_obj.name,
                        'course': course_obj.name
                    }
                    # And throw it in the list
                    section_list.append(sec)
                    # end
                    # end
        # end
        # Add the list of sections the student is in to our template
        template_values['sections'] = section_list
        # Set the template html page
        template = utils.jinja_env().get_template('students/home.html')
        # And render it
        self.response.write(template.render(template_values))
        # end get

# end class HomePage
