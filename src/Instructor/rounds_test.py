"""
rounds_test.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding discussion rounds.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: March 07, 2016

--------------------


"""
import json

import webapp2
from google.appengine.api import users

from src import models
from src import utils

class RoundsTest(webapp2.RequestHandler):
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
        template = utils.jinja_env().get_template('instructor/rounds_test.html')
        self.response.write(template.render(template_values))
    #end get

    def post(self):
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(models.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        #end

        # Now, let's grab the number of rounds and duration from the page
        num_of_rounds = int(self.request.get('dics_num'))
        action = self.request.get('action')

        if not action:
            # Error if not
            utils.error('Invalid arguments: action is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add':
                # Grab the duration
                duration_of_round = int(self.request.get('duration'))
                # Send the number and duration to the add rounds function
                self.add_rounds(num_of_rounds, duration_of_round, instructor)
            #elif action == 'delete':
                # Send the id of the round to be deleted
            #    self.delete_round(round_id)
            #elif action == 'change':
                # Send the new number of rounds requested
            #    self.change_num_of_rounds(num_of_rounds)
            else:
                # Send an error if any other action is supplied
                utils.error('Unexpected action: ' + action, handler=self)
            #end
        #end
    #end post

    def add_rounds(self, num_of_rounds, duration, instructor):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab the current round
        current_round = int(self.request.get('round'))

        # TODO: Figure out how the start time is going to be determined.
        # As it currently stands, there is nowhere to enter a "start-time"
        # or "end-time" for the rounds.
        # This needs fixed in the view.
        start_times = json.loads(self.request.get('times'))

        # Now let's just loop over the number of rounds
        for i in range(num_of_rounds - 1):
            # Start by creating a new round object with the correct parameters
            # TODO: Description and anonymity will only be set during an edit
            new_round = models.Round(parent=section.key, id=current_round)
            new_round.deadline = start_times[i]
            new_round.number = current_round
            # And save our object
            new_round.put()
            # And increment the current round for next iteration
            current_round += 1
        #end
        utils.log('Success, {0} rounds added.'.format(num_of_rounds - 1), type='S', handler=self)
    #end add_rounds

#end class RoundsTest
