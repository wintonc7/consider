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

* Open a new tab or browser window and visit [http://localhost:8080](http://localhost:8080)

This is the web application running on your local machine.

#Server Setup

If you will be pushing updates or would like to test CONSIDER in a simulated production environment you can follow the steps in this section.  You will need a [Google/Gmail Account](https://accounts.google.com/signup) to continue.

###Create a Google App Engine project

If you are pushing update for CONSIDER you may skip these steps.

1. If you have not already done so, sign into your Google account

2. Visit the [Google App Engine project selector](https://console.cloud.google.com/projectselector/appengine)

3. Enter a **Project Name**

4. Agree to the **Terms of Service**

5. Click **Create**

6. Make note of your new project's *Project ID*.  This ID will be necessary for pushing up changes and is also the unique subdomain for your web applcation (i.e., http://your-webapp-ID.appspot.com).  You can always visit your [Google Dashboard](https://console.cloud.google.com/home/dashboard) to retrieve it.

###Pushing your code to the server

1. If you have not already done so, unpack the zip file containing the project code

2. Open a terminal window

3. Navigate to the directory where you unpacked the project code

4. Push the code to the server with the following command:

    `$ appcfg.py -A <your-webapp-ID> update consider/`

    **NOTE:** If you are signed into a Google account within your browser other than the one you are using for CONSIDER, you may need to run the following command to switch accounts:

    `$ appcfg.py -A <your-webapp-ID> update --no_cookies consider/`

5. A browser window should open

6. In the browser window sign into the Google account you are using for CONSIDER

7. The code should now upload to the server (check terminal for status messages)

8. Visit `http://your-webapp-ID.appspot.com` to see if your code has updated

**NOTE:** If the server does not seem to be running your code, make sure the server is running the correct version (this is defined in your **app.yaml** in the root directory).  You can visit the following URL to gverify the correct version is being served.

`https://console.cloud.google.com/appengine/versions?project=`**`your-webapp-ID`**
