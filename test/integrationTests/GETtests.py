import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

 #setting up new test data separate from above tests
    #set up new test admin, instructor, course, section and student
try:   
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
except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag") 
    #==================[END: GET TESTING]==================