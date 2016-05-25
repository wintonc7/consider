"""
rounds.py
~~~~~~~~~~~~~~~~~
Implements the APIs for Instructor control of adding discussion rounds.

- Author(s): Rohit Kapoor, Swaroop Joshi, Tyler Rasor, Dustin Stanley
- Last Modified: March 07, 2016

--------------------


"""
import json
import datetime
import jinja2

import webapp2
from google.appengine.api import users
from google.appengine.api import mail

from src import models
from src import utils


def str_to_date(date_string, format="%Y-%m-%dT%H:%M"):
    return utils.convert_time(date_string)


def since_epoch(date):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (date - epoch).total_seconds() * 100.0


jinja2.filters.FILTERS['str_to_date'] = str_to_date
jinja2.filters.FILTERS['since_epoch'] = since_epoch

class Rounds(webapp2.RequestHandler):
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
            # Send the current time stamp back to the view to do comparisons with
            template_values['now'] = datetime.datetime.now()
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
            utils.error('Error! Invalid arguments: action is null', handler=self)
        else:
            # Now switch on the action
            if action == 'add':
                # Only the lead-in or summary are listed as an 'add' action
                self.add_leadin_summary(instructor)
            elif action == 'add_disc':
                # Now, let's grab the number of rounds and duration from page
                num_of_rounds = int(self.request.get('total_discussions'))
                duration_of_round = int(self.request.get('duration'))
                # And grab the buffer time between rounds
                buffer_bw_rounds = 0 #int(self.request.get('buffer_time'))
                # Send the number and duration to the add rounds function
                self.add_rounds(num_of_rounds, duration_of_round, instructor, buffer_bw_rounds)
            elif action == 'delete':
                # Send the id of the round to be deleted
                round_id = int(self.request.get('round_id'))
                self.delete_round(instructor, round_id)
            elif action == 'change':
                # Send the id of the round to be edited
                round_id = int(self.request.get('round_id'))
                self.edit_round(instructor, round_id)
            elif action == 'start':
                # Simply kick off the first round
                self.start_rounds(instructor)
                # Send mail to students
                # Grab section object and instructor email to pass to email function
                email_course, email_section = utils.get_course_and_section_objs(self.request, instructor)
                # Grab the message of the email
                message = self.request.get('message')
                # Grab the subject of the email
                subject = self.request.get('subject')
                utils.send_mail(instructor.email, email_section, subject, message)

                #-----------------update recent course   modified by Wuwei Lan
                email_course.recent_section=email_section.name
                print email_section.name+"******************"
                email_course.put()
                # -----------------update recent course   modified by Wuwei Lan

            else:
                # Send an error if any other action is supplied
                utils.error('Error! Unexpected action: ' + action, handler=self)
            #end
        #end
    #end post


    def add_leadin_summary(self, instructor):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)

        # Before anything, we need to check that the deadline is in the future
        end_time = self.request.get('time')
        if datetime.datetime.now() > utils.convert_time(end_time):
            # Send an error if so and exit
            utils.error('Error! Cannot create deadline in the past.', handler=self)
            return
        #end

        # Build the round object
        round_obj = self.build_round_obj(section)

        # Now grab all of the rounds
        rounds = models.Round.query(ancestor=section.key).fetch()
        # And switch on the type to create our start time
        if round_obj.description == 'leadin':
            self.add_lead_in(round_obj, rounds)
        else:
            # If not a lead-in question, we know it's a summary
            # And check that we're not trying to add a summary as the first
            if not rounds:
                # Send an error if so and return
                utils.error('Error! Summary question cannot be first round added.', handler=self)
                return
            #end

            # First check if we're editing the summary
            if rounds[-1].description == 'summary':
                # And if so, grab the deadline of the round before the summary
                last_time = rounds[-2].deadline
                # And remove the old summary from the database
                rounds[-1].put().delete()
            else:
                # Otherwise, grab the deadline of the previous round
                last_time = rounds[-1].deadline
            #end

            # Let's check that the deadline doesn't conflict with the last round
            if utils.convert_time(round_obj.deadline) <= utils.convert_time(last_time):
                # Send an error if so and return
                utils.error('Error! Cannot set end time of summary before end of last discussion.', handler=self)
                return
            #end
            # Set start time of summary as the deadline of the last round
            round_obj.starttime = last_time
        #end

        # Now save the round to the database
        round_obj.put()
        # And grab all the rounds one last time
        rounds = models.Round.query(ancestor=section.key).fetch()
        # And update the section rounds attribute if necessary
        self.update_section_rounds(rounds[-1].number, section)
        # And send our success message
        # utils.log('Success, round added.', type='Success!', handler=self)
        utils.log(
            'Success! Round added.',
            type='S', handler=self)
    #end add_leadin_summary

    def build_round_obj(self, section):
        # Start by grabbing the end time and round number from the page
        end_time = self.request.get('time')
        round_num = int(self.request.get('round'))
        # Now create our new round object
        round_obj = models.Round(parent=section.key, id=round_num)
        # And set the deadling and round number and quiz type
        round_obj.deadline = end_time
        round_obj.number = round_num
        round_obj.is_quiz = True
        # Try and grab the buffer time from the page
        start_buffer = self.request.get('startBuffer')
        print("\n\n\n\n" + str(start_buffer) + "\n\n\n\n")
        # Check if it exists (i.e. only on the lead-in round)
        if start_buffer:
            # And set the property on the object if so
            round_obj.buffer_time = int(start_buffer)
        #end

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

        return round_obj
    #end build_round_obj

    def add_lead_in(self, round_obj, rounds):
        # We'll simply use unix epoch as the start time for leadin questions
        epoch = datetime.datetime(1970,1,1)
        round_obj.starttime = utils.convert_time(epoch)
        # Now we need to check if there are more rounds
        if rounds and len(rounds) > 1:
            # Discussion directly after the lead-in will always be index 1
            # If new lead-in deadline conflicts, shift rounds
            if utils.convert_time(round_obj.deadline) >= utils.convert_time(rounds[1].starttime):
                # Now we need to shift all of the rounds, so loop over them
                for i in range(1, len(rounds)):
                    # And grab the duration of the round
                    duration = self.get_duration(rounds[i].starttime, rounds[i].deadline)
                    # And grab the deadline of the previous round
                    new_start = utils.convert_time(rounds[i-1].deadline)
                    # Add the 24 hour padding for the first round
                    if i == 1:
                        new_start = utils.convert_time(round_obj.deadline)
                        new_start += datetime.timedelta(hours = 24)
                    #end
                    # And set our new start and end times and save
                    rounds[i].starttime = utils.convert_time(new_start)
                    rounds[i].deadline = utils.convert_time(new_start + duration)
                    rounds[i].put()
                #end
            #end
        #end
    #end add_lead_in

    def add_rounds(self, num_of_rounds, duration, instructor, buffer_bw_rounds):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab all of the rounds for this section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('Error! No lead-in question exists; cannot add new rounds yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # We'll need this later on when doing the buffer stuff
        # if rounds_buffer < 0
        #     # Make sure the buffer value is positive
        #     utils.error('Error! Buffer value must be greater than 0.', handler=self)
        #     # And redirect
        #     return self.redirect('/')
        # #end

        # Copy the summary round if it exists
        summary = self.copy_summary(section, rounds, num_of_rounds)
        # If it exists, pop it off the list
        if summary:
            rounds.pop()
        #end

        # Now create all the new rounds
        new_rounds = self.create_new_rounds(section, rounds, num_of_rounds, duration, buffer_bw_rounds)

        # And update the summary round
        self.update_summary(summary, new_rounds)
        # Now update the number of rounds attribute of the section
        self.update_section_rounds(new_rounds[-1].number, section)

        # Now grab all of the rounds again
        rounds = models.Round.query(ancestor=section.key).fetch()
        # And send a success message
        utils.log('Successfully added {0} new rounds.'.format(num_of_rounds), type='Success!', handler=self)
    #end add_rounds

    def create_new_rounds(self, section, rounds, num_of_rounds, duration, buffer_bw_rounds):
        # Now grab the current last round number
        current_last_round = rounds[-1].number
        # We need the end time of the last round currently in this section
        last_time = rounds[-1].deadline
        # And grab the start buffer from the previous round
        start_buffer = rounds[-1].buffer_time
        # Now we need to compute new start and end times for the new rounds
        start_times, end_times = self.get_new_times(last_time, num_of_rounds, duration, buffer_bw_rounds, start_buffer)
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

    def get_new_times(self, start, num, duration, delay, start_buffer):
        # First, we need to get the start time into something we can work with
        start = utils.convert_time(start)
        # Grab the current time
        start += datetime.timedelta(hours = start_buffer)

        # Ok, now we need to create our new start and end times list
        start_times = list()
        end_times = list()
        # And loop the correct number of times
        for i in range(num):
            # Create start and end times with the given duration and delay
            start_time = start + datetime.timedelta(hours = i * duration + i * delay)
            end_time = start + datetime.timedelta(hours = (i+1) * duration + (i+1) * delay)
            # And add to our arrays
            start_times.append(utils.convert_time(start_time))
            end_times.append(utils.convert_time(end_time))
        #end
        return start_times, end_times
    #end get_new_times



    def delete_round(self, instructor, round_id):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab all of the rounds for this section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('Error! No lead-in question exists; cannot add new rounds yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # Now shift all the rounds and remove the round with the input id
        self.shift_rounds(rounds, round_id)

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
        # And send a success message
        utils.log('Successfully deleted round {0}'.format(round_id), type='Success!', handler=self)
    #end delete_rounds

    def shift_rounds(self, rounds, round_id):
        # Now look for the round with the input id
        for i in range(len(rounds)):
            # Look for the correct round
            if rounds[i].number == round_id:
                # Now loop over the rest of the rounds (except the very last)
                for j in range(i, len(rounds) - 1):
                    # We're just dealing with normal discussions
                    # and we can just shift the values directly
                    rounds[j].description = rounds[j+1].description
                    rounds[j].is_anonymous = rounds[j+1].is_anonymous
                    # No need to move anything quiz related since it isn't
                    # a lead-in or summary question
                    # Lastly, we need to compute the duration to move over
                    duration = self.get_duration(rounds[j+1].starttime, rounds[j+1].deadline)
                    # Keep the old start time of rounds[j] and calculate
                    # the new end time
                    this_start = utils.convert_time(rounds[j].starttime)
                    rounds[j].deadline = utils.convert_time(this_start + duration)
                    # And store it to the database
                    rounds[j].put()
                #end
                # Break out of the outter loop
                break
            #end
        #end
    #end shift_rounds



    def edit_round(self, instructor, round_id):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab all of the rounds for this section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('Error! No lead-in question exists; cannot add new rounds yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # Now grab the inputs from the page
        description = self.request.get('description')
        # And convert the start and end times to datetime objects
        start_time = utils.convert_time(self.request.get('start_time'))
        deadline = utils.convert_time(self.request.get('deadline'))

        # Loop over the rounds to find the one we're trying to edit
        for i in range(len(rounds)):
            if rounds[i].number == round_id:
                # First, let's set the description
                rounds[i].description = description

                # Now, let's grab the deadline of the previous round
                previous_end = rounds[i-1].deadline
                # And convert it to datetime object
                previous_end = utils.convert_time(previous_end)
                # Check if the new start time is BEFORE the previous round's
                # end time
                if start_time < previous_end:
                    # Send an error if so
                    utils.error('Error! Cannot set new start time earlier than \
                            deadline of round {0}.'.format(i-1), handler=self)
                    # And exit
                    break
                #end
                # Otherwise, the new start time doesn't overlap; we can set it
                rounds[i].starttime = utils.convert_time(start_time)
                # And now set the new deadline for this round
                rounds[i].deadline = utils.convert_time(deadline)

                # Now, check to see if there's a rounds we need to propogate to
                if i != len(rounds) - 1:
                    # Grab the start time of the next round
                    next_start = utils.convert_time(rounds[i+1].starttime)
                    # If the new deadline isn't the same as the next start time
                    if deadline != next_start:
                        # We need to move the start and end times of the rest
                        # of the rounds, so loop over them
                        for j in range(i+1, len(rounds)):
                            # First, get the duration of the round
                            duration = self.get_duration(rounds[j].starttime, rounds[j].deadline)
                            # Now set the new start time to be the
                            # deadline of the previous round
                            rounds[j].starttime = rounds[j-1].deadline
                            # And calculate and set the new end time
                            new_deadline = utils.convert_time(rounds[j].starttime) + duration
                            rounds[j].deadline = utils.convert_time(new_deadline)
                            # And save it back to the database
                            rounds[j].put()
                        #end
                    #end
                #end
                # And commit the changes to the database
                rounds[i].put()
                # Since we've done our updating, break the loop
                utils.log('Successfully updated round {0}.'.format(round_id), type='S', handler=self)
                break
            #end
        #end
    #end



    def start_rounds(self, instructor):
        # So first we need to get at the course and section
        course, section = utils.get_course_and_section_objs(self.request, instructor)
        # And grab all of the rounds for this section
        rounds = models.Round.query(ancestor=section.key).fetch()
        # The view requires at least a lead-in question to add rounds, but check
        if not rounds:
            # Send an error if no rounds exist for this section
            utils.error('Error! No lead-in question exists; cannot start yet.', handler=self)
            # And redirect
            return self.redirect('/')
        #end

        # Now simply turn on the first round
        section.current_round = 1
        section.put()
        # And send a success message
        utils.log('Successfully started the first round.', type='Success!', handler=self)
    #end


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
            duration = self.get_duration(summary.starttime, summary.deadline)
            # Now grab the new start time from the last round's deadline
            new_start = utils.convert_time(rounds[-1].deadline)
            # Set the summary start time to be the end of the last new round
            summary.starttime = utils.convert_time(new_start)
            summary.deadline = utils.convert_time(new_start + duration)
            # And save it to the database and add to our list
            summary.put()
            rounds.append(summary)
        #end
    #end update_summary

    def update_section_rounds(self, num, section):
        # Update the section rounds attribute if necessary
        if num != section.rounds:
            section.rounds = num
            section.put()
        #end
    #end update_section_rounds

    def get_duration(self, start, end):
        duration = 0
        # First, check what type start and end were sent as
        if type(start) != datetime.datetime:
            start = utils.convert_time(start)
        #end
        if type(end) != datetime.datetime:
            end = utils.convert_time(end)
        #end

        # Simply return the end time minus the start time
        return (end - start)
    #end get_duration

#end class Rounds
