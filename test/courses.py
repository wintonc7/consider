import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

#===========[START: testing /courses]===================
try:    
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
except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
    #===========[END: testing /courses]===================