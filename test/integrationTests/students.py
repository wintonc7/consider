import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

 #===========[START: testing /students]===================
try:    
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

except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")   
    #===========[END: testing /students]===================