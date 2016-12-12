import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

#===========[START: testing /rounds]===================
  
try:    
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

except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
    #toggle_anon
    #toggle_round_structure
    #===========[END: testing /rounds]===================