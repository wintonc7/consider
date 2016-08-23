import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime

class TestServer:
    #class for instantiating the test server
    def __init__(self,datastore_path,application_path):
        #desired location for the datastore of the test server
        self.temp_datastore_path = datastore_path
        #path to google app engine application directory
        self.app_path = application_path
        #this is going to be the process object for the server
        self.server_process = None

    #should not be called if a local development server is already started
    def startServer(self):
        # the following "with" block starts the local development server as a subprocess
        # we don't want the output of the test server,
        # so stderr and stdout are directed to /dev/null
        with open(os.devnull, 'w') as fp:
            # make sure this file is deleted
            del_p = subprocess.Popen(["rm",self.temp_datastore_path],stdout=fp,stderr=fp)
            del_p.wait()
            # security on user input important here ***
            # ie if user input "/home/consider && <malicious shell command>" it could be bad
            # start local server, specifying location for new datastore
            self.server_process = subprocess.Popen(["dev_appserver.py","--datastore_path="+self.temp_datastore_path,self.app_path,"--clear_datastore"],stdout=fp,stderr=fp)
            #TODO: check if dev_appserver is in path, if it's not fail
        TestServer.wait_for_server()

    #terminates test server and deletes datastore
    def quit_server(self):
        self.server_process.terminate()
        del_p = subprocess.Popen(["rm",self.temp_datastore_path])
        del_p.wait()

    def stop_server(self):
        self.server_process.terminate()
        self.server_process = None

    def resume_server():
        self.server_process = subprocess.Popen(["dev_appserver.py","--datastore_path="+temp_datastore_path,self.app_path],stdout=fp,stderr=fp)
        TestServer.wait_for_server()

    @staticmethod
    def wait_for_server():
        for i in range(0,15):
            sleep(1)
            if TestServer.isAServerRunning():
                break
            if i == 14:
                print("ERROR: server did not start in 15 seconds")

    @staticmethod
    def isAServerRunning():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1',8080))
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result2 = sock.connect_ex(('127.0.0.1',8000))
        sock.close()
        if result == 0 and result2 == 0:
            return True
        else:
            return False

#config section
temp_datastore_path ="/tmp/test-tmp-datastore"
#==================[START: initial checks]==================
#check to make sure we are running tests on a valid platform
if ("linux" not in sys.platform) and ("darwin" not in sys.platform):
    print("Sorry, this test script was designed to work with linux, not "+sys.platform)
    exit()

#check number of arguments
if len(sys.argv) < 2:
	print("not enough arguments!")
	print("$ ./test.py <path to consider>")
	exit()

#get user arguments
program = sys.argv[0]
path_to_consider = sys.argv[1]

# check user input for security
# some security on user input (look for: ***)
if (";" or "&" or "|" or " ") in path_to_consider:
	print("not a valid path to consider: ;, &, |, and whitespace are not allowed")
	exit()
if not os.path.exists(path_to_consider):
    print("not a valid path to consider: path <"+path_to_consider+"> does not exist")
    print("try using an absolute path. eg:")
    print("./test.py /home/millstev/summer16/capstone/consider")
    exit()

#check to see if a server is already started
if TestServer.isAServerRunning():
   print("Please terminate the local server before running the test script")
   exit()
else:
   print("Starting test server...")

#==================[END: initial checks]==================
#==================[START: set up test server]==================
#in this section, we start a local development server

test_server = TestServer(temp_datastore_path,path_to_consider)
test_server.startServer()

#==================[END: set up test server]==================
#==================[START: prepare to run tests]==================

#in this section we define methods for use in the test cases
#most of these test methods are implemented via webscraping the local dev server

import requests
import json

#this session will be used in the tests
session = requests.Session()
#DEFINE METHODS USED FOR TESTS

#used for logging in
#second parameter True if we want to log in as administrator
def login(email_addr,isAdmin):
    url_string = "http://localhost:8080/_ah/login?email="+email_addr
    if isAdmin:
        url_string = url_string + "&admin=True"
    url_string = url_string + "&action=Login&continue=http://localhost:8080/"
    r = session.get(url_string)
    sleep(0.15)

#used to log out
def logout():
    session.get("http://localhost:8080/_ah/login?continue=http://localhost:8080/courses&action=logout")

def admin_post(datainput):
    r = session.post("http://localhost:8080/admin",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: admin post request responded with "+str(r))
    sleep(0.15)
    return r

def courses_post(datainput):
    r = session.post("http://localhost:8080/courses",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: courses post request responded with "+str(r))
    sleep(0.15)
    return r

def sections_post(datainput):
    r = session.post("http://localhost:8080/sections",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: sections post request responded with "+str(r))
    sleep(0.15)
    return r

def rounds_post(datainput):
    r = session.post("http://localhost:8080/rounds",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: rounds post request responded with "+str(r))
    sleep(0.15)
    return r

def students_post(datainput):
    r = session.post("http://localhost:8080/students",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: students post request responded with "+str(r))
    sleep(0.15)
    return r

def student_rounds_post(datainput):
    r = session.post("http://localhost:8080/student_rounds",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: student_rounds post request responded with "+str(r))
    sleep(0.15)
    return r

def student_rounds_get(key):
    return session.get("http://localhost:8080/student_rounds?section="+key)

def groups_post(datainput):
    r = session.post("http://localhost:8080/groups",data=datainput)
    if not ("200" or "401" in str(r)):
        print("error: groups post request responded with "+str(r))
    sleep(0.15)
    return r

def studentRespond(response,key):
    data={"option":"option1","comm":response,"section":key}
    return student_rounds_post(data)

def addSection(course_name,section_name):
    data={"course":course_name,"section":section_name,"action":"add"}
    return sections_post(data)

def modifyNumberOfGroups(num,course_name,section_name):
    data={"groups":num,"course":course_name,"section":section_name,"action":"add"}
    return groups_post(data)

def addInitialQuestion(duetime,question,numberQuestions,course,section):
    options = ["test question"]*numberQuestions
    options = str(options).replace("'",'"')
    data={"course":course.upper(),"section":section.upper(),"time":duetime,"question":question,"number":numberQuestions,"round":"1","roundType":"initial","startBuffer":"0","options":options,"action":"add"}
    return rounds_post(data)

def addDiscussionRounds(num,duration,course,section):
    data = {"total_discussions":num,"duration":duration,"course":course,"section":section,"action":"add_disc"}
    return rounds_post(data)

def deleteDiscussionRound(round_id,course,section):
    data = {"round_id":round_id,"course":course,"section":section,"action":"delete"}
    return rounds_post(data)

def changeDiscussionRound(round_id,course,section,description,deadline,starttime):
    data = {"round_id":round_id,"course":course,"section":section,"description":description,"roundType":"discussion","action":"change","deadline":deadline,"start_time":starttime}
    return rounds_post(data)

def addCourse(course_name):
    data={"name":course_name,"action":"add"}
    return courses_post(data)

def addStudents(emails,course,section):
    data = {"emails":str(emails).replace("'",'"'),"course":course,"section":section,"action":"add"}
    return students_post(data)

def removeStudent(email):
    data = {"email":email,"action":"remove"}
    return students_post(data)

#this method is confusing: the point is to locate and extract a token from the response
#this token is needed as a session cookie for authenticated requests
#basically, in order for a POST request to console to be successful, it must include this token as a cookie
def get_xsrf_token():
    req = requests.get("http://localhost:8000/console")
    reg = re.compile("xsrf_token.*\}")
    reg2 = re.compile("\w+")
    result = reg2.findall(str(reg.findall(req.text)[0]).split()[1])[0]
    if not result:
        print("ERROR: could not find xsrf_token!")
        return ""
    else:
        return result
xsrf_token = get_xsrf_token()

#this method is a way to send a console script to the interactive console webpage
#the point is so that the database may be queried programmatically
#the ans.text response will only contain what would have been printed out on the console
#so include print statements in the script in order to get the value in the response
def console(script):
    data = {"code":script,"module_name":"default","xsrf_token":xsrf_token}
    ans = requests.post("http://localhost:8000/console",data=data)
    return ans.text.strip()

#goes to the student home page and gets a list of keys for displayed sections
def get_section_key_list():
    answer = []
    req = session.get("http://localhost:8080/student_home")
    reg = re.compile("redirect.*btn-block")
    result = reg.findall(req.text)
    for r in result:
        spl = r.split("'")
        answer.append(spl[1])
    return answer

def print_passed(num):
    print("\t\ttest "+str(num)+" passed")

def print_failed(num,errormsg):
    print("\t\ttest "+str(num)+" FAILED: "+errormsg)

def get_instructor_count():
    script = "from src import model\nprint(len(model.Instructor.query().fetch()))\n"
    result = console(script)
    return int(result)

def get_course_count(instructor_email):
    script = "from src import model\ninstructor = model.Instructor.query(model.Instructor.email=='"+instructor_email+"').fetch()[0]\ncourses = model.Course.query(ancestor=instructor.key).fetch()\nprint(len(courses))"
    result = console(script)
    return int(result)

def get_total_course_count():
    script = "from src import model\ncourses = model.Course.query().fetch()\nprint(len(courses))"
    result = console(script)
    return int(result)

def get_total_response_count():
    script = "from src import model\nresponses = model.Response.query().fetch()\nprint(len(responses))"
    result = console(script)
    return int(result)

def get_section_count(instructor_email):
    script = "from src import model\ninstructor = model.Instructor.query(model.Instructor.email=='"+instructor_email+"').fetch()[0]\nsections = model.Section.query(ancestor=instructor.key).fetch()\nprint(len(sections))"
    result = console(script)
    return int(result)

def get_group_count(instructor_email,course,section):
    script = "from src import model\n"
    script += "instructor = model.Instructor.query(model.Instructor.email=='"+instructor_email+"').fetch()[0]\n"
    script += "sections = model.Section.query(ancestor=instructor.key).fetch()\n"
    script += "for s in sections:\n"
    script += " if s.name == '"+section.upper()+"':\n"
    script += "  print(s.groups)\n"
    script += "  break\n"
    result = console(script)
    return int(result)

def get_total_section_count():
    script = "from src import model\nsections = model.Section.query().fetch()\nprint(len(sections))"
    result = console(script)
    return int(result)

def get_total_round_count():
    script = "from src import model\nrounds = model.Round.query().fetch()\nprint(len(rounds))"
    result = console(script)
    return int(result)

def get_total_student_count():
    script = "from src import model\nstudents = model.Student.query().fetch()\nprint(len(students))"
    result = console(script)
    return int(result)

def addInstructor(email):
    data = {'action':'add','email':email}
    admin_post(data)

def toggleInstructor(email):
    data = {'action':'toggle','email':email}
    admin_post(data)

def toggleCourse(coursename):
    data = {'action':'toggle','name':coursename}
    courses_post(data)

def toggleSection(coursename,sectionname):
    data = {'action':'toggle','course':coursename,'section':sectionname}
    sections_post(data)

def isInstructorActive(email):
    script = "from src import model\ninstructor = model.Instructor.query(model.Instructor.email=='"+email+"').fetch()[0]\nprint(instructor.is_active)"
    result = console(script)
    if "True" in result:
        return True
    elif "False" in result:
        return False
    else:
        print("error: could not retrieve instructor")

def isCourseActive(name):
    script = "from src import model\ncourse = model.Course.query(model.Course.name=='"+name.upper()+"').fetch()[0]\nprint(course.is_active)"
    result = console(script)
    if "True" in result:
        return True
    elif "False" in result:
        return False
    else:
        print("error: could not retrieve course")

def isSectionActive(coursename,sectionname):
    script = "from src import model\ncourse = model.Course.query(model.Course.name=='"+coursename.upper()+"').fetch()[0]\nsection = model.Section.query(ancestor=course.key).fetch()\nfor sec in section:\n if (sec.name == '"+sectionname.upper()+"'):\n  print(sec.is_active)\n"
    result = console(script)
    if "True" in result:
        return True
    elif "False" in result:
        return False
    else:
        print("error: could not retrieve section")

def endCurrentRound(course,section):
    data={"action":"end-current-round","course":course,"section":section}
    r = rounds_post(data)

def startRounds(course,section,):
    data={"action":"start","course":course,"section":section}
    rounds_post(data)

def getDeadline(round_id):
    script = "from src import model\n"
    script += "rounds = model.Round.query(model.Round.number == "+str(round_id)+").fetch()[0]\n"
    script += "print(rounds.deadline)\n"
    return console(script)

def getDescription(round_id):
    script = "from src import model\n"
    script += "rounds = model.Round.query(model.Round.number == "+str(round_id)+").fetch()[0]\n"
    script += "print(rounds.description)\n"
    return console(script)

def getStarttime(round_id):
    script = "from src import model\n"
    script += "rounds = model.Round.query(model.Round.number == "+str(round_id)+").fetch()[0]\n"
    script += "print(rounds.starttime)\n"
    return console(script)

#returns 0 if no round is current
def getCurrentRoundNum(section):
    script = "from src import model\n"
    script += "sections = model.Section.query(model.Section.name=='"+section.upper()+"').fetch()[0]\n"
    script += "print(sections.current_round)\n"
    ans = console(script)
    if ans == "": ans = "0"
    return int(console(script))

def canAddInstructor():
    canAddInstructor.prev_inst_num += 1
    start_count = get_instructor_count()
    addInstructor('instructor'+str(canAddInstructor.prev_inst_num)+'@gmail.com')
    after_count = get_instructor_count()
    return (after_count != start_count)
canAddInstructor.prev_inst_num = 1000

def canToggleInstructor(email):
    toggleInstructor(email)
    afterToggle = isInstructorActive(email)
    #we toggle twice so the instructor goes back to the original toggle state
    toggleInstructor(email)
    afterToggle2 = isInstructorActive(email)
    return (afterToggle != afterToggle2)

def canToggleCourse(coursename):
    toggleCourse(coursename)
    afterToggle = isCourseActive(coursename)
    #we toggle twice so the instructor goes back to the original toggle state
    toggleCourse(coursename)
    afterToggle2 = isCourseActive(coursename)
    return (afterToggle != afterToggle2)

def canToggleSection(coursename,sectionname):
    toggleSection(coursename,sectionname)
    afterToggle = isSectionActive(coursename,sectionname)
    #we toggle twice so the instructor goes back to the original toggle state
    toggleSection(coursename,sectionname)
    afterToggle2 = isSectionActive(coursename,sectionname)
    return (afterToggle != afterToggle2)


inst_directories = ["/courses","/group_responses","/groups","/responses","/rounds","/sections","/students"]
std_directories = ["/student_home","/student_rounds"]
admin_directories = ["/admin"]
#leave a user type as None if you don't want to run tests for that user type
def testGET(admin,instructor,student,course,section,situation_string):
    print("\trunning GET tests for the situation <"+situation_string+">")
    #instructor GET testing
    if instructor is not None:
        login(instructor,False)
        #TEST to make sure instructor gets 200 when expected
        for dir in inst_directories:
            r = session.get("http://localhost:8080"+dir)
            if not "200" in str(r):
                print("\t\t\tFAILED (expected 200): instructor got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
            else:
                print("\t\t\tpassed: instructor got 200 for "+dir)
        #TEST to make sure instructor gets 401 as expected
        for dir in admin_directories:
            r = session.get("http://localhost:8080"+dir)
            if not "401" in str(r):
                print("\t\t\tFAILED (expected 401): instructor got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
            else:
                print("\t\t\tpassed: instructor got 401 for "+dir)
        logout()
    #student GET testing
    if student is not None:
        login(student,False)
        #TEST to make sure student gets 200 when expected
        for dir in std_directories:
            #we need to treat /student_rounds differently because the GET request url contains the section key
            if dir == "/student_rounds":
                keys = get_section_key_list()
                if len(keys) > 0:
                    r = student_rounds_get(keys[0])
                    if not "200" in str(r):
                        print("\t\t\tFAILED (expected 200): student got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
                    else:
                        print("\t\t\tpassed: student got 200 for "+dir)
            else:
                r = session.get("http://localhost:8080"+dir)
                if not "200" in str(r):
                    print("\t\t\tFAILED (expected 200): student got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
                else:
                    print("\t\t\tpassed: student got 200 for "+dir)
        #TEST to make sure student gets 401 as expected
        for dir in inst_directories:
            r = session.get("http://localhost:8080"+dir)
            if not ("302" in str(r.history) and "student_home" in r.url):
                print("\t\t\tFAILED (expected 302 to student_home): url response was <"+r.url+">, history was <"+str(r.history)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
            else:
                print("\t\t\tpassed: student got 302, 200 for "+dir)
        #TEST to make sure student gets 401 as expected
        for dir in admin_directories:
            r = session.get("http://localhost:8080"+dir)
            if not "401" in str(r):
                print("\t\t\tFAILED (expected 401): student got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
            else:
                print("\t\t\tpassed: student got 401 for "+dir)
        logout()
    #admin GET testing
    if admin is not None:
        login(admin,True)
        #TEST to make sure admin gets 200 when expected
        for dir in admin_directories:
            r = session.get("http://localhost:8080"+dir)
            if not "200" in str(r):
                print("\t\t\tFAILED (expected 200): admin got <"+str(r)+"> when sending a GET request to <"+dir+"> when <"+situation_string+">")
            else:
                print("\t\t\tpassed: admin got 200 for "+dir)
        logout()

#==================[END: prepare to run tests]==================
#==================[START: run tests]==================

try:
    #set up test admin, instructor, course, section and student
    login("test-admin@gmail.com",True)
    addInstructor("test-instructor@gmail.com")
    logout()
    if (get_instructor_count()==1):
        print("test-admin created successfully")
        print("test-instructor created successfully")
    login("test-instructor@gmail.com",False)
    addCourse("TEST-COURSE")
    if (get_course_count("test-instructor@gmail.com")==1):
        print("test-course created successfully")
    addSection("TEST-COURSE","TEST-SECTION")
    if (get_section_count("test-instructor@gmail.com")==1):
        print("test-section created successfully")
    students = ["test-student@gmail.com","test-student2@gmail.com"]
    addStudents(students,"TEST-COURSE","TEST-SECTION")
    if (get_total_student_count()>0):
        print("test-student created successfully")

    #===========[START: testing /admin]===================
    #testing POST requests to admin page
    print("testing /admin")
    print("\t testing POST action = add")
    #TEST: see if admin can add instructor
    test_number = 1
    login("test-admin@gmail.com",True)
    if(canAddInstructor()):
        print_passed(test_number)
    else:
        print_failed(test_number,"admin was unable to add an instructor")
    logout()
    test_number+=1
    #TEST: see if instructor can add instructor
    login("test-instructor@gmail.com",False)
    if(canAddInstructor()):
        print_failed(test_number,"incorrect permissions: instructor was able to add an instructor")
    else:
        print_passed(test_number)
    logout()
    test_number += 1
    #TEST: see if student can add instructor
    login("test-student@gmail.com",False)
    if(canAddInstructor()):
        print_failed(test_number,"incorrect permissions: student was able to add an instructor")
    else:
        print_passed(test_number)
    logout()
    test_number += 1
    print("\t testing POST action = toggle")
    #TEST: see if admin can toggle instructor
    login("test-admin@gmail.com",True)
    if(canToggleInstructor("test-instructor@gmail.com")):
        print_passed(test_number)
    else:
        print_failed(test_number,"admin was unable to toggle an instructor")
    logout()
    test_number+=1
    #TEST: see if instructor can add instructor
    login("test-instructor@gmail.com",False)
    if(canToggleInstructor("test-instructor@gmail.com")):
        print_failed(test_number,"incorrect permissions: instructor was able to toggle an instructor")
    else:
        print_passed(test_number)
    logout()
    test_number += 1
    #TEST: see if student can add instructor
    login("test-student@gmail.com",False)
    if(canToggleInstructor("test-instructor@gmail.com")):
        print_failed(test_number,"incorrect permissions: student was able to toggle an instructor")
    else:
        print_passed(test_number)
    logout()
    test_number += 1
   
    #===========[END: testing /admin]===================
    #===========[START: testing /students]===================
    print("testing /students")
    print("\t testing POST action = add")
    test_number = 1
    #TEST: see if instructor can add student
    login("test-instructor@gmail.com",False)
    startcount = get_total_student_count()
    students = ["test-student3@gmail.com","test-student4@gmail.com"]
    addStudents(students,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_student_count()
    if(aftercount - startcount == 2):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not add students")
    logout()
    test_number += 1
    #TEST: see if student can add student
    login("test-student@gmail.com",False)
    startcount = get_total_student_count()
    students = ["test-student5@gmail.com","test-student6@gmail.com"]
    addStudents(students,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_student_count()
    if(aftercount != startcount):
        print_failed(test_number,"permissions error: student was able to add students")
    else:
        print_passed(test_number)
    logout()
    test_number += 1

    #TEST: see if instructor can add duplicate students
    login("test-instructor@gmail.com",False)
    startcount = get_total_student_count()
    students = ["test-student3@gmail.com","test-student4@gmail.com"]
    addStudents(students,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_student_count()
    if(aftercount == startcount):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor was able to add duplicate students")
    logout()
    test_number += 1

    #TEST: see if instructor can add duplicate students when adding at same time
    login("test-instructor@gmail.com",False)
    startcount = get_total_student_count()
    students = ["test-student7@gmail.com","test-student7@gmail.com"]
    addStudents(students,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_student_count()
    #check greater than 1 because we should only add 1 or 0
    if(aftercount - startcount > 1):
        print_failed(test_number,"instructor was able to add duplicate students by sending duplicates in a single request")
    else:
        print_passed(test_number)
    logout()
    test_number += 1
    print("\t testing POST action = remove")

    #TODO: the below test is not testing the right thing
    #test to see if an instructor can remove a student
    '''
    login("test-instructor@gmail.com",False)
    addStudents(["test-student8@gmail.com"],"TEST-COURSE","TEST-SECTION")
    before_remove = get_total_student_count()
    removeStudent("test-student8@gmail.com")
    after_remove = get_total_student_count()
    if (before_remove - after_remove == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not remove a student: TODO: seems this test is not testing the right thing")
    test_number += 1
    #investigate: maybe removing just removes the student from the section, not from the entire thing
    #result: yes it does (remove from section, not from everything).
    '''
    #test to see if a student can remove a student
    login("test-instructor@gmail.com",False)
    addStudents(["test-student9@gmail.com"],"TEST-COURSE","TEST-SECTION")
    logout()
    login("test-student@gmail.com",False)
    before_remove = get_total_student_count()
    removeStudent("test-student9@gmail.com")
    after_remove = get_total_student_count()
    if (before_remove == after_remove):
        print_passed(test_number)
    else:
        print_failed(test_number,"permissions error: student was able to remove a student")
    
    #===========[END: testing /students]===================
    #===========[START: testing /courses]===================
    print("testing /courses")
    print("\t testing POST action = add")
    test_number = 1
    #TEST: see if instructor can add course
    login("test-instructor@gmail.com",False)
    startcount = get_total_course_count()
    addCourse("COURSEXYZ")
    aftercount = get_total_course_count()
    if(aftercount - startcount == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not add a course")
    logout()
    test_number += 1

    #TEST: see if instructor can add duplicate course
    login("test-instructor@gmail.com",False)
    startcount = get_total_course_count()
    addCourse("COURSEXYZ2")
    middlecount = get_total_course_count()
    addCourse("COURSEXYZ2")
    aftercount = get_total_course_count()
    if(aftercount - startcount == 1 and middlecount == aftercount):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor was able to add duplicate courses")
    logout()
    test_number += 1

    #TEST: see if student can add course
    login("test-student@gmail.com",False)
    startcount = get_total_course_count()
    addCourse("COURSEXYZ")
    aftercount = get_total_course_count()
    if(aftercount - startcount == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"permissions error: student could add a course")
    logout()
    test_number += 1  

    print("\t testing POST action = toggle")
    #TEST: see if instructor can toggle a course
    login("test-instructor@gmail.com",False)
    if(canToggleCourse("TEST-COURSE")):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor was unable to toggle a course")
    logout()
    test_number+=1

    #TEST: see if student can toggle a course
    login("test-student@gmail.com",False)
    if(canToggleCourse("COURSEXYZ")):
        print_failed(test_number,"permissions error: student was able to toggle a course")
    else:
        print_passed(test_number)
    logout()
    test_number+=1

    #===========[END: testing /courses]===================
    #===========[START: testing /sections]===================
    print("testing /sections")
    print("\t testing POST action = add")
    test_number = 1
    #TEST: see if instructor can add section
    login("test-instructor@gmail.com",False)
    startcount = get_total_section_count()
    addSection("TEST-COURSE","SECTIONXYZ")
    aftercount = get_total_section_count()
    if(aftercount - startcount == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not add a section")
    logout()
    test_number += 1
    #TEST: see if instructor can add section to a course that doesn't exisit
    login("test-instructor@gmail.com",False)
    startcount = get_total_section_count()
    addSection("TEST-COURSEasdfsd","SECTIONXYZ")
    aftercount = get_total_section_count()
    if(aftercount - startcount == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could add a section to a course that doesn't exist")
    logout()
    test_number += 1

    #TEST: see if instructor can add duplicate section
    login("test-instructor@gmail.com",False)
    startcount = get_total_section_count()
    addSection("TEST-COURSE","SECTIONXYZ2")
    middlecount = get_total_section_count()
    addSection("TEST-COURSE","SECTIONXYZ2")
    aftercount = get_total_section_count()
    if(aftercount - startcount == 1 and middlecount == aftercount):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor was able to add duplicate sections")
    logout()
    test_number += 1

    #TEST: see if student can add section
    login("test-student@gmail.com",False)
    startcount = get_total_section_count()
    addSection("TEST-COURSE","STUDENTSECTION")
    aftercount = get_total_section_count()
    if(aftercount - startcount == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"permissions error: student could add a section")
    logout()
    test_number += 1  

    print("\t testing POST action = toggle")
    #TEST: see if instructor can toggle a section
    login("test-instructor@gmail.com",False)
    if(canToggleSection("TEST-COURSE","TEST-SECTION")):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor was unable to toggle a section")
    logout()
    test_number+=1

    #TEST: see if student can toggle a section
    login("test-student@gmail.com",False)
    if(canToggleSection("TEST-COURSE","TEST-SECTION")):
        print_failed(test_number,"permissions error: student was able to toggle a section")
    else:
        print_passed(test_number)
    logout()
    test_number+=1

    #===========[END: testing /sections]===================
    #===========[START: testing /rounds]===================
    print("testing /rounds")
    #add
    print("\t testing POST action = add")
    test_number = 1
    #TEST: see if instructor can add rounds
    login("test-instructor@gmail.com",False)
    startcount = get_total_round_count()
    #make due tomorrow
    duetime = datetime.datetime.now()+datetime.timedelta(hours=24)
    duetime = duetime.strftime("%Y-%m-%dT%H:%M")
    question = "sample question"
    numberQuestions = 4
    course = "TEST-COURSE"
    section = "TEST-SECTION"
    addInitialQuestion(duetime,question,numberQuestions,course,section)
    aftercount = get_total_round_count()
    if(aftercount - startcount == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not add a initial question")
    logout()
    test_number += 1

    #TEST: see if instructor can add another, duplicate initial question
    login("test-instructor@gmail.com",False)
    startcount = get_total_round_count()
    #make due tomorrow
    duetime = datetime.datetime.now()+datetime.timedelta(hours=24)
    duetime = duetime.strftime("%Y-%m-%dT%H:%M")
    question = "sample question"
    numberQuestions = 4
    course = "TEST-COURSE"
    section = "TEST-SECTION"
    addInitialQuestion(duetime,question,numberQuestions,course,section)
    aftercount = get_total_round_count()
    if(aftercount - startcount == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could add duplicate initial questions")
    logout()
    test_number += 1

    #TEST: see if student can add initial question
    login("test-student@gmail.com",False)
    startcount = get_total_round_count()
    #make due tomorrow
    duetime = datetime.datetime.now()+datetime.timedelta(hours=24)
    duetime = duetime.strftime("%Y-%m-%dT%H:%M")
    question = "sample question"
    numberQuestions = 4
    course = "TEST-COURSE"
    section = "TEST-SECTIONXYZ"
    addInitialQuestion(duetime,question,numberQuestions,course,section)
    aftercount = get_total_round_count()
    if(aftercount - startcount == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could add duplicate initial questions")
    logout()
    test_number += 1
    #add_disc
    #TEST: see if instructor can add discussion rounds
    login("test-instructor@gmail.com",False)
    startcount = get_total_round_count()
    addDiscussionRounds(10,1,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_round_count()
    if(aftercount - startcount == 10):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not add 10 discussion rounds")
    logout()
    test_number += 1
    #start
    login("test-instructor@gmail.com",False)
    startRounds("TEST-COURSE","TEST-SECTION")
    if(getCurrentRoundNum("TEST-SECTION")==1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not start rounds")
    logout()
    test_number+=1
    #end-current-round
    #TEST: see if instructor can end current round
    login("test-instructor@gmail.com",False)
    num1 = getCurrentRoundNum("TEST-SECTION")
    endCurrentRound("TEST-COURSE","TEST-SECTION")
    num2 = getCurrentRoundNum("TEST-SECTION")
    if(num1 != num2):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not end current round")
    logout()
    test_number += 1

    #delete
    #TEST: see if instructor can delete a round
    login("test-instructor@gmail.com",False)
    startcount = get_total_round_count()
    deleteDiscussionRound(4,"TEST-COURSE","TEST-SECTION")
    aftercount = get_total_round_count()

    if (startcount - aftercount == 1):
        print_passed(test_number)
    else:
        print_failed(test_number, "instructor could not delete a discussion round")

    logout()
    test_number += 1
    #change

    #TEST: see if instructor can change a round
    login("test-instructor@gmail.com",False)
    # Note: Need to exclude the last 3 characters (:00) that correspond to seconds.
    deadline = getDeadline(6).strip().replace(" ", "T")[:-3]
    starttime = getStarttime(6).strip().replace(" ","T")[:-3]
    description = "changed!"
    responseFromPost = changeDiscussionRound(6,"TEST-COURSE","TEST-SECTION",description,deadline,starttime)
    if str(description) == str(getDescription(6)):
        print_passed(test_number)
    else:
        #uncomment the following two lines to see why it failed
        # print(responseFromPost.text)
        # exit()
        print_failed(test_number,"instructor could not edit a discussion round's description")
    logout()
    test_number += 1

    #toggle_anon
    #toggle_round_structure
    #===========[END: testing /rounds]===================
    #===========[START: testing /groups]===================
    print("testing /groups")
    #add
    print("\t testing POST action = add")
    test_number = 1
    #TEST: see if instructor can modify number of groups
    login("test-instructor@gmail.com",False)
    initial = get_group_count("test-instructor@gmail.com","TEST-COURSE","TEST-SECTION")
    modifyNumberOfGroups(initial+1,"TEST-COURSE","TEST-SECTION")
    after = get_group_count("test-instructor@gmail.com","TEST-COURSE","TEST-SECTION")
    if(after - initial == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"instructor could not modify the number of groups to have one more group")
    logout()
    test_number += 1

    #update
    #this method is testing below: function is to add students to groups and thus must be done after students have done something 
    #===========[END: testing /groups]===================
    #setting up new test data separate from above tests
    #set up new test admin, instructor, course, section and student
    print("setting up new data for testing student views...")
    login("test-admin@gmail.com",True)
    #add instructor
    addInstructor("s-test-instructor@gmail.com")
    logout()
    login("s-test-instructor@gmail.com",False)
    #add course
    addCourse("S-TEST-COURSE")
    #add section
    addSection("S-TEST-COURSE","S-TEST-SECTION")
    students = ["s-test-student@gmail.com","s-test-student2@gmail.com"]
    #add students to the created section
    addStudents(students,"S-TEST-COURSE","S-TEST-SECTION")
    duetime = datetime.datetime.now()+datetime.timedelta(hours=24)
    duetime = duetime.strftime("%Y-%m-%dT%H:%M")
    question = "sample question"
    numberQuestions = 4
    course = "S-TEST-COURSE"
    section = "S-TEST-SECTION"
    #add initial question a discussion rounds
    addInitialQuestion(duetime,question,numberQuestions,course,section)
    addDiscussionRounds(10,1,"S-TEST-COURSE","S-TEST-SECTION")
    #start the rounds
    startRounds("S-TEST-COURSE","S-TEST-SECTION")
    logout()
    #testing POST requests to admin page
    test_number = 1
    print("testing /student_home")
    login("s-test-student@gmail.com",False)
    keys = get_section_key_list()
    if len(keys) != 1:
        print_failed(test_number,"student did not have the right amount of sections displayed")
    else:
        print_passed(test_number)

    print("testing /student_rounds")

    #TEST: see if responding increases total number of responses by 1
    initial = get_total_response_count()
    studentRespond("test response",keys[0])
    after = get_total_response_count()
    if(after - initial == 1):
        print_passed(test_number)
    else:
        print_failed(test_number,"student could not submit response")
    logout()
    test_number+=1

    #TEST: see if modifying the response changes the total number of responses
    login("s-test-student@gmail.com",False)
    initial = get_total_response_count()
    studentRespond("test response modified",keys[0])
    after = get_total_response_count()
    if(after - initial == 0):
        print_passed(test_number)
    else:
        print_failed(test_number,"student modified existing response, but it changed the total number of responses")
    logout()
    test_number+=1

    #TODO: test /student_rounds POST on discussion and final rounds
    #TODO: check if the student submitted a response

    #==================[START: GET TESTING]==================
    print("Starting to test GET requests")
    getAdmin = "get-admin@gmail.com"
    getInst = "get-instructor@gmail.com"
    getStd = "get-student@gmail.com"
    getStd2 = "get-student2@gmail.com"
    getCourse = "GET-TEST-COURSE"
    getSection = "GET-TEST-SECTION"
    #######
    #setting up new test data separate from above tests
    #set up new test admin, instructor, course, section and student
    login(getAdmin,True)
    #add instructor
    addInstructor(getInst)
    testGET(getAdmin,getInst,None,getCourse,getSection,"brand new instructor added")
    logout()
    login(getInst,False)
    #add course
    addCourse(getCourse)
    testGET(getAdmin,getInst,None,getCourse,getSection,"course added without section, no students")
    login(getInst,False)
    #add section
    addSection(getCourse,getSection)
    testGET(getAdmin,getInst,None,getCourse,getSection,"course and section, no students")
    login(getInst,False)
    students = [getStd,getStd2]
    #add students to the created section
    r = addStudents(students,getCourse,getSection)
    print(r.text)
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"fresh course, section, and student added")
    login(getInst,False)
    duetime = datetime.datetime.now()+datetime.timedelta(hours=24)
    duetime = duetime.strftime("%Y-%m-%dT%H:%M")
    question = "sample question"
    numberQuestions = 4
    course = getCourse
    section = getSection
    #add initial question and discussion rounds
    addInitialQuestion(duetime,question,numberQuestions,course,section)
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"initial question added but no discussion rounds")
    login(getInst,False)
    addDiscussionRounds(10,1,getCourse,getSection)
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"initial question and discussion rounds added but not started")
    login(getInst,False)
    #start the rounds
    startRounds(getCourse,getSection)
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"initial question and discussion rounds added and started")
    logout()
    login(getStd,False)
    keys = get_section_key_list()
    studentRespond("test response",keys[0])
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"initial question and discussion rounds added and student responded to initial question")
    logout()
    login(getInst,False)
    endCurrentRound(getCourse,getSection)
    testGET(getAdmin,getInst,getStd,getCourse,getSection,"student responded to initial question, and the round ended and students were not added to groups yet")
    #==================[END: GET TESTING]==================

except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
#==================[END: run tests]==================
