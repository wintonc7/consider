# CONSIDER

## What is CONSIDER?
CONSIDER is a web app that uses the idea of cognitive conflict to facilitate small group discussion within students on a 
given topic. Research shows that when learners engage with peers in critical discussion of ideas concerning which they 
have different understandings, that contributes very effectively to learners developing deep understanding of the concepts 
involved.

Another unique feature of CONSIDER is its asynchronous, structured, rounds-based discussion. Due to this, each student gets 
to, and has to, respond to the posts of every group member exactly once per round. She can revisit her post before the round 
ends (typically 24 hours) to make any modifications. This ensures that each student, whether quick on her feet, or prefers 
to think through subtle ramifications before posting, or anything in-between, participates equally effectively. In addition, 
frivolous posts and flame wars are completely avoided.

CONSIDER also implements anonymity of the students while the discussion is going on. Due to this, students participate more 
freely, and the effectiveness of the discussion is not compromised by any gender/ethnic/other preconceptions some students 
may have.

The web app is free to use and is developed using [Google App Engine](https://cloud.google.com/appengine/) and Python. It is 
scalable and has responsive web frontend. As a result, it can be accessed from practically any device with great ease. All 
you need is a valid Google ID to use the app.

### Download and install

Download the code for the app at http://tiny.cc/considerzip (**TODO** fix the link; where to host?)

##### Prerequisites
- Python 2.7
- **TODO** Python packages/dependencies
- [Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)
- To launch on the web, [Google Cloud](https://cloud.google.com) account; Not needed if you plan to runtest locally

Following instructions focus on the testing the app on localhost. To upload it to the cloud, user should follow the steps
described at [Uploading your application](https://cloud.google.com/appengine/docs/python/gettingstartedpython27/uploading).


- Download and unzip the code. 
- Start Google App Engine Launcher that comes with the SDK, and add the application to the launcher. 
- Choose appropriate ports. (We will assume the default port `8080` for the rest of this document.)
- `Run` the app. 

###### Admin Role
- In any web browser, go to `localhost:8080/secretlandingpage`. When promted for login, use `test@example.com` and check the box for administrator.
- Once logged in, add an instructor email (e.g., `teacher@ex.com`).
- You can activate/deactivate the instructor.
- Log out when done.

###### Instructor Role
**TODO**

###### Student Role
**TODO**
