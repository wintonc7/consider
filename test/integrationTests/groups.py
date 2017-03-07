import socket
import sys
import os
import subprocess
from time import sleep
import traceback
import re
import datetime
from __main__ import *

#===========[START: testing /groups]===================
    
try:    
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
except:
    #prints the stack trace when there is an error
    print("exception thrown.")
    traceback.print_exc()
finally:
    if "--stay-alive" not in sys.argv:
        test_server.quit_server()
    else:
        print("leaving server running because of --stay-alive flag")
    #update
    #this method is testing below: function is to add students to groups and thus must be done after students have done something 
    #===========[END: testing /groups]===================