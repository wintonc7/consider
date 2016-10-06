import csv

import webapp2
from google.appengine.api import users

from src import model, utils


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
                template_values['num_std']=len(current_section.students)
            if current_section.rounds:
                template_values['rounds'] = current_section.rounds
            if current_section.groups:
                template_values['num_group']=current_section.groups
        from src import config
        template_values['documentation'] = config.DOCUMENTATION
        template = utils.jinja_env().get_template('instructor/show_responses.html')
        self.response.write(template.render(template_values))

class DataExport(webapp2.RequestHandler):

    def post(self):
        course_name = self.request.get('course')
        section_name = self.request.get('section')
        selector=self.request.get('action')
        #print selector
        instructor_tmp = utils.check_privilege(model.Role.instructor)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        instructor.export_course=course_name.upper()
        course = model.Course.get_by_id(course_name, parent=instructor.key)
        course.export_section=section_name.upper()
        section = model.Section.get_by_id(section_name.upper(),parent=course.key)
        section.export_info=selector
        instructor.put()
        course.put()
        section.put()
        #print ('finished')

    def get(self):
        self.response.headers['Content-Type'] = 'application/txt'
        #out = self.makeit()
        #self.response.write(out.getvalue())
        instructor_tmp = utils.check_privilege(model.Role.instructor)
        writer = csv.writer(self.response.out)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        course = model.Course.get_by_id(instructor.export_course, parent=instructor.key)
        section = model.Section.get_by_id(course.export_section, parent=course.key)
        students=section.students
        writer.writerow([instructor.export_course, course.export_section, ])
        selector=section.export_info
        selector=selector.split()
        count=0
        export_rounds={}
        print selector
        while count<len(selector):
            if int(selector[count]) in export_rounds.keys():
                export_rounds[int(selector[count])].append(int(selector[count+1]))
            else:
                export_rounds[int(selector[count])]=[]
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            count += 2
        print export_rounds
        rounds=model.Round.query(ancestor=section.key).fetch()
        for i in export_rounds.keys():
            writer.writerow(['This is student '+students[i].email+' :',] )
            for j in export_rounds[i]:
                writer.writerow(['Round'+str(j), ])
                responses = model.Response.query(ancestor=rounds[j-1].key).fetch()
                for resp in responses:
                    if resp.student==students[i].email:
                        #print 'test@@@'
                        writer.writerow([resp.student, resp.comment, resp.response, ])
        #writer.writerow([instructor.export_course, course.export_section, instructor.email, ])
        print 'Hello!'

class HtmlExport(webapp2.RequestHandler):
    def get(self):
        instructor_tmp = utils.check_privilege(model.Role.instructor)
        instructor = model.Instructor.get_by_id(instructor_tmp.email)
        course = model.Course.get_by_id(instructor.export_course, parent=instructor.key)
        section = model.Section.get_by_id(course.export_section, parent=course.key)
        students = section.students
        selector=section.export_info
        selector=selector.split()
        count=0
        export_rounds={}
        #print selector
        while count<len(selector):
            if int(selector[count]) in export_rounds.keys():
                export_rounds[int(selector[count])].append(int(selector[count+1]))
            else:
                export_rounds[int(selector[count])]=[]
                export_rounds[int(selector[count])].append(int(selector[count + 1]))
            count += 2
        #print export_rounds
        rounds = model.Round.query(ancestor=section.key).fetch()
        template_values={}
        output_students=[]
        output_seq_rounds={}
        output_options={}
        output_comments={}
        output_responses={}
        output_summary={}
        #export_rounds contain {key, value}, where key is student and value is round
        for i in export_rounds.keys():
            output_students.append(students[i])
            output_seq_rounds[students[i].email]=[]
            output_options[students[i].email]=[]
            output_comments[students[i].email]=[]
            output_responses[students[i].email]=[]
            output_summary[students[i].email]=[]
            for j in export_rounds[i]:
                output_seq_rounds[students[i].email].append(j)
                flag=False
                responses = model.Response.query(ancestor=rounds[j-1].key).fetch()
                for resp in responses:
                    if resp.student==students[i].email:
                        output_options[students[i].email].append(resp.option)
                        output_comments[students[i].email].append(resp.comment)
                        output_responses[students[i].email].append(resp.response)
                        output_summary[students[i].email].append(resp.summary)
                        flag=True
                if flag==False:
                    output_options[students[i].email].append('NA')
                    output_comments[students[i].email].append('NA')
                    output_responses[students[i].email].append('NA')
                    output_summary[students[i].email].append('NA')
        template_values['students']=output_students
        template_values['seq_rounds']=output_seq_rounds
        template_values['comments']=output_comments
        template_values['responses']=output_responses
        template_values['option']=output_options
        template_values['summary']=output_summary
        template = utils.jinja_env().get_template('instructor/show_html_responses.html')
        self.response.write(template.render(template_values))
