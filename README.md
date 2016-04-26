#Local Environment Setup

In order to develop and test the CONSIDER Web App locally you will need to install the Google App Engine SDK for Python on your development machine. Please note Google App Engine is under active development so these documents may not be completely accurate at the time of reading. If you are having difficulty performing the steps for setup contained in this document, you may wish to visit [Google's Cloud Platform page](http://cloud.google.com) and searching for Google App Engine.

###Download and install the necessary software

* [Download and install Python 2.7](http://www.python.org/download/)

* [Download and install the Google App Engine SDK.](https://developers.google.com/appengine/downloads)

###Running the server on localhost
* Unpack the zip file containing the project code.

* Open up a terminal.

* Navigate to the directory where you unpacked the project code.

* Run the following command: `$ dev_appserver.py consider/`

* Open a browser window and visit [http://localhost:8000](http://localhost:8000)

This is the Google App Engine console on your local machine.

Open a new tab or browser window and visit [http://localhost:8080](http://localhost:8080)

This is the web application running on your local machine.
