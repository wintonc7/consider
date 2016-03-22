"""
rounds_test.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding discussion rounds.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor
- Last Modified: March 07, 2016

--------------------


"""
import json
import datetime

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
        num_of_rounds = int(self.request.get('total_discussions'))
        action = self.request.get('action')

        if not action:
            # Error if not
            utils.error('Invalid arguments: action is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add_disc':
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

        # First, grab all the rounds for this current section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('No lead-in question exists; cannot add new rounds yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # Now grab the current last round
        current_last_round = rounds[-1].number
        # We need the end time of the last round currently in this section
        last_time = rounds[-1].deadline
        # Now we need to compute new start and end times for the new rounds
        end_times = self.get_end_times(last_time, num_of_rounds, duration, 0)

        # Now let's just loop over the number of rounds
        for i in range(num_of_rounds):
            # TODO: Description and anonymity will only be set during an edit

            # And increment the current round for this iteration
            current_last_round += 1
            # Create a new rounds object
            new_round = models.Round(parent=section.key, id=current_last_round)
            # Set the deadline
            new_round.deadline = end_times[i]
            # And the round number
            new_round.number = current_last_round
            # And save our object
            new_round.put()
        #end
        utils.log('Success, {0} rounds added.'.format(num_of_rounds), type='S', handler=self)
    #end add_rounds

    def get_end_times(self, start, num, duration, delay):
        # First, we need to get the start time into something we can work with
        start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M")

        # Ok, now we need to create our new end times list
        end_times = list()
        # And loop the correct number of times
        for i in range(1,num+1):
            end_time = start + datetime.timedelta(hours = i * duration + delay)
            end_times.append(end_time.isoformat()[:-3])
        #end
        return end_times
    #end

#end class RoundsTest
