"""
rounds.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Student role in the app.

- Author(s): Rohit Kapoor, Swaroop Joshi
- Last Modified: Sep 2, 2016

--------------------


"""

import datetime
import json

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

from src import model, utils


def find_prev_round_responses(current_round):
    prev_round_number = current_round.number - 1
    section = current_round.key.parent().get()
    req_round = model.Round.get_by_number(section_key=section.key, number=prev_round_number)
    utils.log('req_round = Round#' + str(req_round.number))
    return model.Response.query(ancestor=req_round.key).fetch() if req_round else None


def quiz_view_template(student, rround, template_values):
    # Grab the response for this round by this student
    response = model.Response.get_by_id(student.email, parent=rround.key)
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


def group_comments(group, section, previous_round):
    # Init an empty list for holding the comments
    comments = []
    did_not_participate = []
    # Now loop over the members in the group
    for student_email in group.members:
        # Grab each response from the previous round
        response = model.Response.get_by_id(student_email, parent=previous_round.key)

        # Get the student's info
        s = section.find_student_info(student_email)

        if response:
            comment = {
                'alias': s.alias, 'email': s.email,
                'response': response.comment, 'opinion': response.response
            }
            # Get thumbs if they exist
            if response.thumbs:
                _thumbs = []
                for _email, _value in response.thumbs.iteritems():
                    s_info = section.find_student_info(_email)
                    name = s_info.alias if s_info and section.is_anonymous else _email
                    _thumbs.append((name, _value))  # Add as a tuple
                comment['thumbs'] = sorted(_thumbs)  # Send as sorted tuples

            # If the response has an associated option
            if response.option and response.option != 'NA':
                # Grab the option
                utils.log('response.option = ' + str(response.option))
                opt = int(response.option[-1]) - 1
                comment['option'] = previous_round.quiz.options[opt]
            else:
                comment['option'] = ''  # default

            # And finally add the comment to the list
            comments.append(comment)
        else:
            # Else note down who did not participate
            name = s.alias if section.is_anonymous else s.email
            did_not_participate.append(name)

    utils.log('Comments = ' + str(comments))
    return comments, sorted(did_not_participate)


class Rounds(webapp2.RequestHandler):
    """
    API to redirect a student based on what stage she is in in a particular section:
    initial question, discussion or summary round.

    If no round is active for this section, it redirects to an appropriate error page.
    """

    def get(self):
        # First, check that the logged in user is a student
        student = utils.check_privilege(model.Role.student)
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

    # end get

    def post(self):
        """
        HTTP POST method to submit the response.
        """
        # First, check that the logged in user is a student
        student = utils.check_privilege(model.Role.student)
        if not student:
            # Redirect home if not a student
            return self.redirect('/home')
        # end

        # First, grab the section key from the page
        section_key = self.request.get('section')
        # Double check that we actually got a section key
        if section_key:
            try:
                # Grab the section from the database
                section = ndb.Key(urlsafe=section_key).get()
                # And double check that it's valid

                if section:
                    # Grab the current round from the database
                    current_round = model.Round.get_by_id(section.current_round, parent=section.key)
                    # And double check that it's valid
                    if current_round:
                        # If this is a quiz round or if this section has roudns based discussions,
                        # save it in the usual way
                        if section.has_rounds or current_round.is_quiz:
                            self.save_submission(student, current_round)
                            # TODO - ADD LOGENTRY FOR EDITED RESPONSE
                            # Log submission
                            groups = model.Group.query(ancestor=section.key).fetch()
                            for group in groups:
                                log = model.ActivityLog.query(ancestor=group.key).fetch()
                                log[0].new_entry("Response submitted for round " + str(section.current_round) + ".", student.email)
                        else:
                            # Otherwise, save as a Seq Discussion
                            # 1. Make sure the author email passed from view is same as current student's email
                            author_email = student.email
                            student_info = utils.get_student_info(author_email, section.students)
                            group_id = student_info.group
                            group = model.Group.get_by_id(id=group_id, parent=section.key)

                            # 2. create the post in that group
                            if group:
                                post = model.SeqResponse(parent=group.key)
                                post.author = author_email
                                post.author_alias = student_info.alias
                                post.timestamp = str(datetime.datetime.now())
                                post.text = self.request.get('text')
                                post.index = group.num_seq_responses + 1
                                post.put()

                                # Log submission
                                groups = model.Group.query(ancestor=section.key).fetch()
                                for group in groups:
                                    log = model.ActivityLog.query(ancestor=group.key).fetch()
                                    log[0].new_entry("Response submitted to " + section.name + " discussion.",
                                                     student.email)

                                group.num_seq_responses += 1
                                group.put()
                                utils.log('Post created:' + str(post))
                            else:
                                utils.error('Group is null')
                    else:
                        utils.error('Sorry! The round is not visible, please try again later.', handler=self)
                else:  # section is null
                    utils.error('Section is null', handler=self)
            except Exception as e:
                utils.error(
                    'Sorry! There was some error submitting your response please try again later. Exception: ' + e.message,
                    handler=self)  # TODO: use exceptions in all classes?
        else:
            utils.error('Invalid Parameters: section_key is null', handler=self)

    # end post

    def render_template(self, student, section):
        # update the database to the current round based on time
        database_round = utils.get_current_round(section)
        # Get the requested round number from the page
        current_round = self.request.get('round')
        # Now check that the round number passed in actually exists, and set
        # the requested round number appropriately if not
        if current_round:
            requested_round_number = int(current_round)
        else:
            requested_round_number = section.current_round
        # end

        # Grab the requested round
        requested_round = model.Round.get_by_id(requested_round_number, parent=section.key)
        # And check that it's not null
        if not requested_round:
            # Error if so
            self.redirect('/error?code=104')
        else:
            # Otherwise we need to set up our template values, create empty dict
            template_values = {}
            # Grab the deadline from the requested round
            deadline = requested_round.deadline
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
            # template_values['deadline'] = datetime.datetime.strptime(requested_round.deadline, '%Y-%m-%dT%H:%M')
            template_values['deadline'] = requested_round.deadline
            template_values['sectionKey'] = self.request.get('section')
            template_values['rounds'] = section.current_round
            template_values['num_total_rounds'] = section.rounds
            template_values['show_name'] = not section.is_anonymous

            # Send round names
            if section.has_rounds:
                if section.rounds > 3:
                    disc_round_names = ['Round ' + str(i) for i in range(1, section.rounds - 2)] + ['Latest Posts']
                else:
                    disc_round_names = ['Round 1']
            else:
                disc_round_names = ['Discussion']

            round_names = ['Initial Submission'] + disc_round_names + ['Final Submission']
            template_values['round_names'] = round_names

            logout_url = users.create_logout_url(self.request.uri)
            template_values['logouturl'] = logout_url
            from src import config
            template_values['documentation'] = config.DOCUMENTATION
            if (utils.check_privilege(model.Role.student)):
                template_values['student'] = True
            template_values['curr_page'] = requested_round_number

            # Now we need to check if it's the initial or summary question
            if requested_round.is_quiz:
                # And set template values for quiz round
                quiz_view_template(student, requested_round, template_values)
                # And set the right template
                template = utils.jinja_env().get_template('students/round.html')
            else:
                # Otherwise, set up template values for appropriate discussion round
                if section.has_rounds:
                    self.discussion_view_template(student, section, requested_round_number, template_values)
                    # And set the right template
                    template = utils.jinja_env().get_template('students/discussion.html')
                else:
                    self.seq_discussion_view_template(student, section, template_values)
                    template_values['description'] = requested_round.description
                    template = utils.jinja_env().get_template('students/seq_discussion.html')
            # end
            # Now, render it.
            self.response.write(template.render(template_values))
            # end

    # end render_templates

    def seq_discussion_view_template(self, student, section, template_values):
        student_info = utils.get_student_info(student.email, section.students)
        if student_info:
            # 1. Grab student's alias and group from db
            template_values['alias'] = student_info.alias
            group_id = student_info.group
            group = model.Group.get_by_id(group_id, parent=section.key)
            if group:
                # 2. Extract all the posts in that group from db
                posts = model.SeqResponse.query(ancestor=group.key).order(model.SeqResponse.index).fetch()
                utils.log('Posts: ' + str(posts))
                # 3. Send all the posts to the template
                template_values['posts'] = posts

                # 4. Grab all posts from the previous round (initial)
                initial = model.Round.get_by_id(1, parent=section.key)
                initial_answers, did_not_participate = group_comments(group, section, initial)
                template_values['initial_answers'] = initial_answers
                template_values['did_not_participate'] = did_not_participate

    # end seq_discussion_view_template

    def discussion_view_template(self, student, section, round_number, template_values):
        student_info = utils.get_student_info(student.email, section.students)
        if student_info:
            template_values['alias'] = student_info.alias
            group_id = student_info.group
            group = model.Group.get_by_id(group_id, parent=section.key)
            # Double check that it was found
            if group:
                # Depending on round number, we have to grab from
                if round_number == 1:
                    previous_round = model.Round.get_by_id(1, parent=section.key)
                else:
                    previous_round = model.Round.get_by_id(round_number - 1, parent=section.key)
                # end
                # Now grab all the group comments for the previous round
                comments, did_not_participate = group_comments(group, section, previous_round)
                # Set the template value for all the group comments
                template_values['comments'] = comments
                template_values['did_not_participate'] = did_not_participate
                # Grab the requested round
                requested_round = model.Round.get_by_id(round_number, parent=section.key)
                # Grab the discussion description
                template_values['description'] = requested_round.description
                # And grab the logged in student's response
                stu_response = model.Response.get_by_id(student.email, parent=requested_round.key)
                # Check that they actually answered
                if stu_response:
                    # And set template values to show their previous response
                    template_values['comment'] = stu_response.comment
                    utils.log('Comment = {0}'.format(str(stu_response.comment)))
                    template_values['response'] = ','.join(str(item) for item in stu_response.response)

    # end discussion_view_template

    def save_submission(self, student, current_round):
        # Create a new response object
        response = model.Response(parent=current_round.key, id=student.email)
        # Start by grabbing data from the page
        option = self.request.get('option').lower()
        comment = self.request.get('comm')
        summary = self.request.get('summary')
        res = self.request.get('response')
        # Now check whether we're on a initial or summary or discussion round
        if current_round.is_quiz:
            # If it is, double check that they selected an answer and commented
            if current_round.quiz.options_total > 0 and not (option and comment):
                # if the question had 0 options, it's not an error
                # Error if not
                utils.error('Please select one of the options before submitting.', handler=self)
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
                # utils.error('Invalid Parameters: comment is null or res is not a valid response', handler=self)
                utils.error('Unable to save submission. Please ensure you have entered a comment and that you have entered a valid response.', handler=self)
                return
            # end
            # Now loop over the agree, etc. responses
            for i in range(1, len(res)):
                # And save them in our response object for the db
                response.response.append(res[i])

            # Get all responses of the previous round
            prev_responses = find_prev_round_responses(current_round)

            # Fetch thumbs from the view
            in_thumbs = json.loads(self.request.get('thumbs'))

            if in_thumbs and prev_responses:
                utils.log('in_thumbs = {0}'.format(str(in_thumbs)))

                # Add the thumbs info. to the previous round's responses
                for prev_resp in prev_responses:
                    # _thumbs = []    # Added because there was an error when submitting R1 post on the server;
                                    # could not replicate on dev server
                                    # Error: There was some error submitting your response please try again later.
                                    # Exception: local variable '_thumbs' referenced before assignment
                    if in_thumbs.has_key(prev_resp.student):
                        _thumbs = prev_resp.thumbs.copy()
                        prev_resp.add_to_thumbs(student.email, in_thumbs[prev_resp.student])
                    # utils.log('For' + prev_resp.comment + ', old thumbs = '
                    #           + (str(_thumbs) if _thumbs else 'Empty')
                    #           + ', new thumbs = ' + str(prev_resp.thumbs))
                    # Removed this instead of adding _thumbs = [] at line 385
                    prev_resp.put()

        # Grab the deadline and the current time
        deadline = current_round.deadline
        current_time = datetime.datetime.now()
        # And double check that they've submitted before the deadline ended
        if deadline >= current_time:
            # Set the comment and email, and save in the database
            response.comment = comment
            response.student = student.email
            # utils.log('comment = {0}, response = {1}'.format(comment, response.response))

            response.put()
            utils.log('Your response has been saved. You can edit it any time before the deadline. ',
                      type='Success!', handler=self)

        else:  # Otherwise alert them that time has passed to submit for this round
            utils.error('Sorry, the time for submission for this round has expired \
           and your response was not saved, please wait for the next round.',
                        handler=self)

# end class Rounds
