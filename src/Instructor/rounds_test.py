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

        # Now let's grab the action from the page
        action = self.request.get('action')
        # And check that it was actually passed
        if not action:
            # Error if not
            utils.error('Invalid arguments: action is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add':
                # Only the lead-in or summary are listed as an 'add' action
                self.add_leadin_summary(instructor)
            elif action == 'add_disc':
                # Now, let's grab the number of rounds and duration from the
                num_of_rounds = int(self.request.get('total_discussions'))
                duration_of_round = int(self.request.get('duration'))
                # Send the number and duration to the add rounds function
                self.add_rounds(num_of_rounds, duration_of_round, instructor)
            elif action == 'delete':
                # Send the id of the round to be deleted
                round_id = int(self.request.get('round_id'))
                self.delete_round(instructor, round_id)
            #elif action == 'change':
                # Send the new number of rounds requested
            #    self.change_num_of_rounds(num_of_rounds)
            else:
                # Send an error if any other action is supplied
                utils.error('Unexpected action: ' + action, handler=self)
            #end
        #end
    #end post

    def add_leadin_summary(self, instructor):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)

        # Now grab the values from the post request
        round_num = int(self.request.get('round'))
        end_time = self.request.get('time')
        # Now create our new round object
        round_obj = models.Round(parent=section.key, id=round_num)
        round_obj.deadline = end_time
        round_obj.number = round_num
        # Set the object to be a quiz type
        round_obj.is_quiz = True
        # Now grab all the quiz attributes from the page
        question = self.request.get('question')
        num_options = int(self.request.get('number'))
        options = json.loads(self.request.get('options'))
        # And set the object
        round_obj.quiz = models.Question(options_total=num_options,
                                         question=question, options=options)

        # Now grab the round type (lead-in or summary)
        round_type = self.request.get('roundType')
        # And set the description
        round_obj.description = round_type
        # And switch on the type to create our start time
        if round_type == 'leadin':
            # We'll simply use unix epoch as the start time for leadin questions
            epoch = datetime.datetime(1970,1,1)
            round_obj.starttime = epoch.isoformat()[:-3]
        else:
            # If not a lead-in question, we know it's a summary
            # So, we need to find the end time of the last discussion round
            rounds = models.Round.query(ancestor=section.key).fetch()
            # And check that we're not trying to add a summary as the first
            if not rounds:
                # Send an error if so
                utils.error('Summary question cannot be first round added.', handler=self)
            #end
            last_time = rounds[-1].deadline
            round_obj.starttime = last_time
        #end
        # And update the section rounds attribute if necessary
        self.update_section_rounds(round_obj.number, section)
        round_obj.put()
        utils.log('Success, round added.', type='S', handler=self)
    #end add_leadin_summary

    def add_rounds(self, num_of_rounds, duration, instructor):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)

        # Now, grab all the rounds for this current section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('No lead-in question exists; cannot add new rounds yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # Copy the summary round if it exists
        summary = self.copy_summary(section, rounds, num_of_rounds)
        # If it exists, pop it off the list
        if summary:
            rounds.pop()
        #end

        # Now create all the new rounds
        new_rounds = self.create_new_rounds(section, rounds, num_of_rounds, duration)

        # And update the summary round
        self.update_summary(summary, new_rounds)
        # Now update the number of rounds attribute of the section
        self.update_section_rounds(new_rounds[-1].number, section)

        # Now grab all of the rounds again
        rounds = models.Round.query(ancestor=section.key).fetch()
        # And now send all the rounds back to the view
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(rounds, cls=utils.RoundEncoder))
    #end add_rounds

    def delete_round(self, instructor, id):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)

        # Grab all of the rounds for this section
        rounds = models.Round.query(ancestor=section.key).fetch()

        # Now look for the round with the input id
        for i in range(len(rounds)):
            # Look for the correct round
            if rounds[i].number == id:
                # Now loop over the rest of the rounds (except the very last)
                for j in range(i, len(rounds) - 1):
                    # We're just dealing with normal discussions
                    # and we can just shift the values directly
                    rounds[j].description = rounds[j+1].description
                    rounds[j].is_anonymous = rounds[j+1].is_anonymous
                    # No need to move anything quiz related since it isn't
                    # a lead-in or summary question
                    # Lastly, we need to compute the duration to move over
                    old_end = datetime.datetime.strptime(rounds[j+1].deadline, "%Y-%m-%dT%H:%M")
                    old_start = datetime.datetime.strptime(rounds[j+1].starttime, "%Y-%m-%dT%H:%M")
                    duration = old_end - old_start
                    # Keep the old start time of rounds[j] and calculate
                    # the new end time
                    this_start = datetime.datetime.strptime(rounds[j].starttime, "%Y-%m-%dT%H:%M")
                    rounds[j].deadline = (this_start + duration).isoformat()[:-3]
                    # And store it to the database
                    rounds[j].put()
                #end
                # Break out of the outter loop
                break
            #end
        #end
        # Now let's check if we need to copy a summary question over or not
        if rounds[-1].description == 'summary':
            # Delete the next to last round and remove from the list
            rounds[-2].put().delete()
            rounds.pop(-2)
            # And copy the summary round and update the times
            summary = self.copy_summary(section, rounds, -1)
            # Remove the old summary from the list
            rounds.pop()
            self.update_summary(summary, rounds)
        else:
            # Finally, remove the very last round from the list
            rounds[-1].put().delete()
        #end
        # Since we shifted rounds forward, remove the last round from the list
        rounds.pop()
        # And update the section
        self.update_section_rounds(rounds[-1].number, section)
        # Now grab all of the rounds again
        rounds = models.Round.query(ancestor=section.key).fetch()
        # And now send all the rounds back to the view
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(rounds, cls=utils.RoundEncoder))
    #end

    def update_section_rounds(self, num, section):
        # Update the section rounds attribute if necessary
        if num != section.rounds:
            section.rounds = num
            section.put()
        #end
    #end update_section_rounds

    def copy_summary(self, section, rounds, num_of_rounds):
        summary = None
        # First, check if there's even a summary round to copy
        if rounds[-1].description == 'summary':
            # If so, create a new summary round with those properties
            # But change it to be the last round after adding num_of_rounds
            summary_round_num = rounds[-1].number + num_of_rounds
            summary = models.Round(parent=section.key, id=summary_round_num)
            # Now copy over all the pertinent summary information
            summary.starttime = rounds[-1].starttime
            summary.deadline = rounds[-1].deadline
            summary.number = summary_round_num
            summary.is_quiz = True
            summary.quiz = rounds[-1].quiz
            summary.description = rounds[-1].description
            summary.is_anonymous = rounds[-1].is_anonymous
            # Now remove the summary from the current rounds
            rounds[-1].put().delete()
        #end
        return summary
    #end copy_summary

    def update_summary(self, summary, rounds):
        # And check if a summary round was saved
        if summary:
            # We need to calculate the old duration of the summary round
            old_end = datetime.datetime.strptime(summary.deadline, "%Y-%m-%dT%H:%M")
            old_start = datetime.datetime.strptime(summary.starttime, "%Y-%m-%dT%H:%M")
            duration = old_end - old_start
            # Now grab the new start time from the last round's deadline
            new_start = datetime.datetime.strptime(rounds[-1].deadline, "%Y-%m-%dT%H:%M")
            # Set the summary start time to be the end of the last new round
            summary.starttime = new_start.isoformat()[:-3]
            summary.deadline = (new_start + duration).isoformat()[:-3]
            # And save it to the database and add to our list
            summary.put()
            rounds.append(summary)
        #end
    #end update_summary

    def create_new_rounds(self, section, rounds, num_of_rounds, duration):
        # Now grab the current last round number
        current_last_round = rounds[-1].number
        # We need the end time of the last round currently in this section
        last_time = rounds[-1].deadline
        # Now we need to compute new start and end times for the new rounds
        start_times, end_times = self.get_new_times(last_time, num_of_rounds, duration, 0)
        # Let's keep a list of the newly added rounds
        new_rounds = list()
        # Now let's just loop over the number of rounds
        for i in range(num_of_rounds):
            # And increment the current round for this iteration
            current_last_round += 1
            # Create a new rounds object
            new_round = models.Round(parent=section.key, id=current_last_round)
            # Set the starttime and deadline
            new_round.starttime = start_times[i]
            new_round.deadline = end_times[i]
            # And the round number
            new_round.number = current_last_round
            # And save our object
            new_round.put()
            # And add it to our list
            new_rounds.append(new_round)
        #end
        return new_rounds
    #end create_new_rounds

    def get_new_times(self, start, num, duration, delay):
        # First, we need to get the start time into something we can work with
        start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M")

        # Ok, now we need to create our new start and end times list
        start_times = list()
        end_times = list()
        # And loop the correct number of times
        for i in range(num):
            # Create start and end times with the given duration and delay
            start_time = start + datetime.timedelta(hours = i * duration + i * delay)
            end_time = start + datetime.timedelta(hours = (i+1) * duration + (i+1) * delay)
            # And add to our arrays
            # Use string indexing to remove the seconds from the isoformat
            start_times.append(start_time.isoformat()[:-3])
            end_times.append(end_time.isoformat()[:-3])
        #end
        return start_times, end_times
    #end get_new_times

#end class RoundsTest
