"""
config.py
~~~~~~~~~~~
- Author(s): Swaroop Joshi
- Last Modified: May 30, 2016

--------------------

Some system level configurations.
"""

import os

PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')  # TODO Make sure it works
DEBUG = DEVELOPMENT = not PRODUCTION
# PROJECT_ID = 'rich-brace-854'
# PRODUCTION=os.environ.get('DEVSHELL_PROJECT_ID','').startswith(PROJECT_ID)

# Another Alt.
# import socket
# DEBUG = DEVELOPMENT = socket.gethostname().endswith(".local") # Only on Mac. Change .endswith condition on other platforms
# PRODUCTION = not DEBUG

DOCUMENTATION = "http://swaroopjcse.github.io/consider/"
ADMIN_GUIDE = DOCUMENTATION + "userguides/adminguide.html"  # FIXME not working
INSTRUCTOR_GUIDE = DOCUMENTATION + "userguides/instructorguide.html"
STUDENT_GUIDE = DOCUMENTATION + "userguides/studentguide.html"
