import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

#===========[START: testing /sections]===================
try:   
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
except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
    #===========[END: testing /sections]===================