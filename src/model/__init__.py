from Course import *
from Group import *
from Instructor import *
from ActivityLog import *
from LogEntry import *
from Response import *
from Round import *
from Section import *
from SeqResponse import *
from Student import *
from Grader import *
from Feedback import *


# TODO consistent naming of attributes

class Role:
    def __init__(self):
        pass

    instructor = 'INSTRUCTOR'
    student = 'STUDENT'
    admin = 'ADMIN'
    grader = 'GRADER'
