import csv

import webapp2
from google.appengine.api import users

from src import model, utils
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


class ShowResponses(webapp2.RequestHandler):
    def get(self):
        # First, check that the logged in user is an instructor
        instructor = utils.check_privilege(model.Role.instructor)
        if not instructor:
            # Send them home and short circuit all other logic
            return self.redirect('/')
        # end

        # Otherwise, create a logout url
        logout_url = users.create_logout_url(self.request.uri)
        # And get the course and section names from the page
        course_name = self.request.get('course')
        selected_section_name = self.request.get('section')
        # Grab all the courses and sections for the logged in instructor
        template_values = utils.get_template_all_courses_and_sections(instructor,
                                                                      course_name.upper(),
                                                                      selected_section_name.upper())
        logout_url = users.create_logout_url(self.request.uri)
        template_values['logouturl'] = logout_url
        if 'selectedSectionObject' in template_values:
            # If so, grab that section from the template values
            current_section = template_values['selectedSectionObject']
            if current_section.students:
                # template_values['students'] = current_section.students
                template_values['num_std'] = len(current_section.students)
            if current_section.rounds:
                template_values['rounds'] = current_section.rounds
            if current_section.groups:
                template_values['num_group'] = current_section.groups
        from src import config
        template_values['documentation'] = config.DOCUMENTATION
        template = utils.jinja_env().get_template('instructor/show_responses.html')
        self.response.write(template.render(template_values))


class DataExport(webapp2.RequestHandler):
    def post(self):
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        selector = self.request.get('action')
        # print selector
        instructor_tmp = utils.check_privilege(model.Role.instructor)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        instructor.export_course = course_name.upper()
        course = model.Course.get_by_id(course_name, parent=instructor.key)
        course.export_section = section_name.upper()
        section = model.Section.get_by_id(section_name.upper(), parent=course.key)
        section.export_info = selector
        instructor.put()
        course.put()
        section.put()
        # print ('finished')

    def get(self):
        self.response.headers['Content-Type'] = 'application/txt'
        # out = self.makeit()
        # self.response.write(out.getvalue())
        instructor_tmp = utils.check_privilege(model.Role.instructor)
        writer = csv.writer(self.response.out)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        course = model.Course.get_by_id(instructor.export_course, parent=instructor.key)
        section = model.Section.get_by_id(course.export_section, parent=course.key)
        students = section.students
        writer.writerow([instructor.export_course, course.export_section, ])
        selector = section.export_info
        selector = selector.split()
        count = 0
        export_rounds = {}
        print selector
        while count < len(selector):
            if int(selector[count]) in export_rounds.keys():
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            else:
                export_rounds[int(selector[count])] = []
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            count += 2
        print export_rounds
        rounds = model.Round.query(ancestor=section.key).fetch()
        for i in export_rounds.keys():
            writer.writerow(['This is student ' + students[i].email + ' :', ])
            for j in export_rounds[i]:
                writer.writerow(['Round' + str(j), ])
                responses = model.Response.query(ancestor=rounds[j - 1].key).fetch()
                for resp in responses:
                    if resp.student == students[i].email:
                        # print 'test@@@'
                        writer.writerow([resp.student, resp.comment, resp.response, ])
        # writer.writerow([instructor.export_course, course.export_section, instructor.email, ])

        print 'Hello!' #purpose? use specific print callouts for debugging


class HtmlExport(webapp2.RequestHandler):
    def get(self):

        instructor_tmp = utils.check_privilege(model.Role.instructor)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        course = model.Course.get_by_id(instructor.export_course, parent=instructor.key)
        section = model.Section.get_by_id(course.export_section, parent=course.key)
        students = section.students
        selector = section.export_info
        selector = selector.split()
        ##group = model.Group.get_by_id()
        count = 0
        export_rounds = {}
        # print selector
        while count < len(selector):
            if int(selector[count]) in export_rounds.keys():
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            else:
                export_rounds[int(selector[count])] = []
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            count += 2
        # print export_rounds
        rounds = model.Round.query(ancestor=section.key).fetch()

        groups = model.Group.query(ancestor=section.key).fetch()
        template_values = {}
        output_students = []
        output_seq_rounds = {}
        output_options = {}
        output_comments = {}
        output_responses = {}
        output_summary = {}
        output_posts = []

        ##reference from groups.py
        # if 'selectedSectionObject' in template_values:
        #     # If so, grab that section from the template values
        #     current_section = template_values['selectedSectionObject']
        #     # Check that the current section has at least one round
        #     if current_section.rounds > 0:
        #
        #         # Grab the responses from the initial question
        #         response = model.Response.query(
        #             ancestor=model.Round.get_by_id(1, parent=current_section.key).key).fetch() #fetches round object
        #
        #         no_answer_students = []
        #         # And loop over the students in this section
        #         for stu in current_section.students:
        #             flag = True
        #             # Loop over the responses
        #             for res in response:
        #                 # And check when the response matches the student
        #                 if res.student == stu.email:
        #                     # And set the group of the response to the
        #                     # group of the student who made that response
        #                     res.group = stu.group
        #                     flag = False
        #                     # end
        #             # end
        #             if flag:
        #                 no_answer_students.append(stu)
        #         # end
        #         # Add the responses and current group to the template values
        #         template_values['no_answer_students'] = no_answer_students
        #         template_values['responses'] = response
        #         template_values['group'] = current_section.groups
                # end
        # end
        #student_info = []
        # export_rounds contain {key, value}, where key is student and value is round
        for i in export_rounds.keys():
            output_students.append(students[i])
            #### added for reference
            #student_info[i] = utils.get_student_info(students[i].email, section.students)
            output_seq_rounds[students[i].email] = []
            output_options[students[i].email] = []
            output_comments[students[i].email] = []
            output_responses[students[i].email] = []
            output_summary[students[i].email] = []

            for j in export_rounds[i]:
                output_seq_rounds[students[i].email].append(j)
                flag = False
                if section.has_rounds:  # TODO Also for last and first round in seq
                    responses = model.Response.query(ancestor=rounds[j - 1].key).fetch()
                    output_seq_responses = model.SeqResponse.query(ancestor=groups[j].key).order(
                    model.SeqResponse.index).fetch()
                    for resp in responses:
                        utils.log('resp = ' + str(resp))
                        if resp.student == students[i].email:
                            output_options[students[i].email].append(resp.option)
                            output_comments[students[i].email].append(resp.comment)
                            output_responses[students[i].email].append(resp.response)

                            output_summary[students[i].email].append(resp.summary)
                            flag = True
                    if not flag:
                        output_options[students[i].email].append('NA')
                        output_comments[students[i].email].append('NA')
                        output_responses[students[i].email].append('NA')
                        output_summary[students[i].email].append('NA')



                else:
                    responses = model.SeqResponse.query(ancestor=rounds[j - 1].key).fetch()
                    utils.log('responses = ' + str(responses))
                    for resp in responses:
                        utils.log('resp = ' + str(resp))
                        if resp.author == students[i].email:
                            output_options[students[i].email].append('NA')
                            output_comments[students[i].email].append(resp.text)
                            output_responses[students[i].email].append('NA')
                            output_summary[students[i].email].append('NA')
                            flag = True
                        if not flag:
                            output_options[students[i].email].append('NA')
                            output_comments[students[i].email].append('NA')
                            output_responses[students[i].email].append('NA')
                            output_summary[students[i].email].append('NA')

                for group in groups:

                    posts = model.SeqResponse.query(ancestor=group.key).order(model.SeqResponse.timestamp).fetch()

                    for post in posts:
                        # WHY WAS [POSTS.AUTHOR] = POST.TEXT?
                        if not output_posts.__contains__(post):
                            output_posts.append(post)
                if posts:
                    # Grab the responses from the initial question
                    responses = model.Response.query(
                        ancestor=model.Round.get_by_id(1, parent=section.key).key).fetch()
                    no_answer_students = []
                    for stu in section.students:
                        flag = True
                        # Loop over the responses
                        for res in responses:
                            # And check when the response matches the student
                            if res.student == stu.email:
                                # And set the group of the response to the
                                # group of the student who made that response
                                res.group = stu.group
                                flag = False
                                # end
                            # end
                    if flag:
                        no_answer_students.append(stu)
                     # And loop over the students in this section




                    # end
                    # Add the responses and current group to the template values
                ##copied from students/rounds.py
                # student_info = utils.get_student_info(student.email, section.students)
                # if student_info:
                #     # 1. Grab student's alias and group from db
                #     template_values['alias'] = student_info.alias
                #     group_id = student_info.group
                #     group = model.Group.get_by_id(group_id, parent=section.key)
                #     if group:
                #        # 2. Extract all the posts in that group from db
                #         posts = model.SeqResponse.query(ancestor=group.key).order(
                #         model.SeqResponse.index).fetch()
                #         utils.log('Posts: ' + str(posts))
                #         # 3. Send all the posts to the template
                #         template_values['posts'] = posts
                        #    for resp in seq_responses:
                        #        if resp.author==students[i].email:
                        #            output_comments[students[i].email].append(resp.text)
                        #            flag=True

        #get the sequential initial response
        #output_seq_responses = {}
        #output_seq_responses.initial_response = {}
        #for student in students:
        initial = model.Round.get_by_id(1, parent=section.key)
        initial_answers  = []
        ##from group_responses.py
        # Create a new dict for responses
        resp = {}
        # Loop over the groups (indexed by 1)
        for g in range(1, section.groups + 1):
            # And loop over the rounds (indexed by 1)
            for r in range(1, section.rounds + 1):
                # Now set an empty list for each group and round
                resp['group_' + str(g) + '_' + str(r)] = []
                # end
        # end
        # Loop over the number of rounds (indexed by 1)
        for r in range(1, section.rounds + 1):
            # Grab the responses for that round from the db
            responses = model.Response.query(
                ancestor=model.Round.get_by_id(r, parent=section.key).key).fetch()
            # Double check that the responses actually exist
            if responses:
                # And loop over the responses
                for res in responses:
                    # And loop over the students in this section
                    for s in section.students:
                        # Check that the email of the student
                        # and the email of the response match
                        # and that the student is in a group
                        if s.email == res.student and s.group != 0:
                            # Set the alias of the response
                            res.alias = s.alias
                            # Append the response to the appropriate
                            # group and round
                            resp['group_' + str(s.group) + '_' + str(r)].append(res)
                            break
                            # end
                            # end
                            # end
                            # end
        # end
        # And set the template values for all the responses
        template_values['seq_resp'] = resp
        # end

        for group in groups:
            answer, did_not_participate = group_comments(group, section, initial)
            initial_answers.append(answer)
            final_answers = group_comments(group, section, model.Round.get_by_id(3, parent=section.key))


        template_values['final_answers'] = final_answers
        template_values ['initial_seq'] = initial_answers
        template_values['groups'] = groups
        template_values['posts'] = output_posts
        template_values['students'] = output_students
        template_values['seq_rounds'] = output_seq_rounds
        template_values['comments'] = output_comments
        template_values['responses'] = output_responses
        template_values['option'] = output_options
        template_values['summary'] = output_summary
        template = utils.jinja_env().get_template('instructor/show_html_responses.html')
        self.response.write(template.render(template_values))
