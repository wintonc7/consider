import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

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
    
except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
   
    #===========[END: testing /admin]===================