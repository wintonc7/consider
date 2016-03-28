"""
rounds.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of rounds within the app.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: March 07, 2016

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import models
from src import utils

class Rounds(webapp2.RequestHandler):
    """
    API to retrieve and display the information of *rounds* for the selected course and section.

    By default, the alphabetically first course and first section is selected.
    To look at the rounds for other course/sections, the user can select from the given drop down list.
    """

    def get(self):
        """
        HTTP GET method to retrieve the rounds.
        """
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(models.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        #end

        # Now create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # Grab the course and section name from the webpage
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # And get all the courses and sections for this instructor
        template_values = utils.get_template_all_courses_and_sections(instructor, course_name.upper(), selected_section_name.upper())
        # Now check that the section from the webpage actually corresponded
        # to an actual section in this course, and that the template was set
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            # Set the current active round
            template_values['activeRound'] = current_section.current_round
            # And grab all the rounds for this section
            rounds = models.Round.query(ancestor=current_section.key).fetch()
            # Double check that there are actually rounds already created
            if rounds:
                # And set the template values
                template_values['rounds'] = rounds
                # Create an empty list to hold the discussion rounds
                discussion_rounds = []
                # And loop over all of the rounds for this section
                for r in rounds:
                    # Set the lead-in question
                    if r.number == 1:
                        template_values['leadInQuestion'] = r
                    elif r.is_quiz:
                        # And if not the lead-in question, but still a quiz
                        # it must be the summary round
                        template_values['summaryQuestion'] = r
                    else:
                        # Otherwise, it's just a discussion round
                        discussion_rounds.append(r)
                    #end
                #end
                # Set the discussion round template values
                template_values['discussionRounds'] = discussion_rounds
            #end
            # Check to see if the summary round was set in the template
            if 'summaryQuestion' in template_values:
                # If so, set the next round to the total number of rounds
                template_values['nextRound'] = current_section.rounds
            else:
                # Otherwise, it must be set to the number of rounds plus
                # one (to account for the eventual summary round)
                template_values['nextRound'] = current_section.rounds + 1
            #end
        #end
        # Set the template and render the page
        template_values['logouturl'] = logout_url
        template = utils.jinja_env().get_template('instructor/rounds.html')
        self.response.write(template.render(template_values))
    #end get

    def add_round(self, section):
        # Grab the current round and time from the webpage
        curr_round = int(self.request.get('round'))
        time = self.request.get('time')
        #Create a new round object with those parameters
        round_obj = models.Round(parent=section.key, id=curr_round)
        round_obj.deadline = time
        round_obj.number = curr_round
        # Grab the type of round from the webpage
        round_type = self.request.get('roundType')
        # And check if it's a lead-in or summary round (i.e. a quiz)
        if round_type == 'leadin' or round_type == 'summary':
            # If so, grab the question from the form
            question = self.request.get('question')
            # Set the object to be a quiz type
            round_obj.is_quiz = True
            # And grab the number of options and list of options from the page
            num_options = int(self.request.get('number'))
            options = json.loads(self.request.get('options'))
            # And create and store the question
            round_obj.quiz = models.Question(options_total=num_options,
                                             question=question, options=options)
        elif round_type == 'discussion':
            # Otherwise, if the round is set as discussion,
            # Grab the description and anonymity settings from the page
            description = self.request.get('description')
            anonymity = self.request.get('anonymity')
            # And set those properties in the round object
            round_obj.description = description
            if anonymity != "yes":
                round_obj.is_anonymous = False
            #end
        else:
            # And send an error if any other round type is sent
            utils.error('Unknown round_type passed.', handler=self)
        #end
        # And save the round object into the database
        round_obj.put()
        # Only update the value of total rounds if a new round is created,
        # not when we edit an old round is edited
        if curr_round > section.rounds:
            section.rounds = curr_round
            section.put()
        #end
        utils.log('Success, round added.', type='S', handler=self)
    #end add_round

    def activate_round(self, section):
        # Grab the number for the next round from the page
        next_round = int(self.request.get('round'))
        if section.current_round != next_round:
            # If the selected round is not currently active make it active
            section.current_round = next_round
            section.put()
            utils.log('Success, round active.', type='S', handler=self)
        #end
    #end activate_round

    def post(self):
        """
        HTTP POST method to add the round.
        """

        # TODO Markdown support
        # TODO Timezone support in deadlines

        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(models.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        #end

        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # Grab the action from the page
        action = self.request.get('action')
        # Check that the action is actually supplied
        if not action:
            # Error if not
            utils.error('Invalid argument: action is null', handler=self)
        else:
            # Switch on the action
            if action == 'add':
                # Add
                self.add_round(section)
            elif action == 'activate':
                # Or turn on
                self.activate_round(section)
            else:
                # And error if any other action is provided
                utils.error('Unexpected action: ' + action, handler=self)
            #end
        #end
    #end post

#end class Rounds
