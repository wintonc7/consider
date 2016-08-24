"""
config.py
~~~~~~~~~~~
- Author(s): Swaroop Joshi
- Last Modified: Aug 22, 2016

--------------------

Some system level configurations.
"""

# TODO: Move this file to the root directory

import os

PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Eng')  # TODO Make sure it works
DEBUG = DEVELOPMENT = not PRODUCTION
# PROJECT_ID = 'rich-brace-854'
# PRODUCTION=os.environ.get('DEVSHELL_PROJECT_ID','').startswith(PROJECT_ID)

# Another Alt.
# import socket
# DEBUG = DEVELOPMENT = socket.gethostname().endswith(".local") # Only on Mac. Change .endswith condition on other platforms
# PRODUCTION = not DEBUG

DOCUMENTATION = 'https://github.com/consider-app/consider/wiki'
SETUP_GUIDE = DOCUMENTATION + '/Getting-Started'
INSTRUCTOR_GUIDE = DOCUMENTATION + '/Using-CONSIDER-as-an-Instructor'
STUDENT_GUIDE = DOCUMENTATION + '/Using-CONSIDER-as-a-Student'
