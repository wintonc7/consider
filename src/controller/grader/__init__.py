from .courses import Courses
from .group_responses import GroupResponses
from .show_responses import ShowResponses
from .show_responses import DataExport
from .show_responses import HtmlExport
from .groups import Groups
from .responses import Responses
from .rounds import Rounds
from .sections import Sections

""" The grader class currently exists within the source code
	but as of 12/11/16 it cannot be added to the database.  From
	what I understand, the grader should function properly once
	a developer finds a way to add a grader into the database 
	properly, similarly to how students are added to the database.
	Files for the grader exist in the model and controller.  These
	files are heavily based off of the code for student and instructors
	(essentially the files for graders are code that has been copied 
	and pasted from the already functioning students and instructors).
	So, if you are a developer who is trying to understand the attempted
	implementation of the grader, understand that much of the code is
	IDENTICAL (except for example, replacing the word 'student' with 'grader') 
	to code for the instructor and grader.  From what I understood, 
	the grader should be invited similarly to students, and should
	have similar functionality to an instructor (except for some
	functions such as creating courses or inviting students).  From the
	code added by Capstone team AU16, the grader MAY have unintended
	functionality due to the lack of testing of the grader.  Please do
	not assume that any existing code for the grader has been fully tested.
	In fact, it has not been tested at all, it is simply a start for the
	next team(s) to work on.

	One thing to note about the implementation of the grader is that templates
	have not yet been created for them.  Templates for the grader should appear
	similarly to the templates for instructors, which can be found at
	/src/templates/instructor/..."""