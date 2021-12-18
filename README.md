# README

## Name 

Gerson Personnat

## Project Title

BookSocial

## YouTube Video

https://www.youtube.com/watch?v=0DnWHP_JKtc
## Documentation

### Languages and Frameworks Used: 

Python, Flask (framework), HTML, CSS, and JavaScript.

All the Python packages needed to run the project are listed in requirements.txt. 

### Install VS Code

This project was developed in Visual Studio Code. Download VSCode for your computer at this link: https://code.visualstudio.com/download.

## Install Python - Use this link: https://www.python.org/downloads/

This web app uses Python 3:10.0; Go to the link above and download Python 3.10.0. 

Verify python was installed by using the command python --version (on Windows or Mac). You should see that "Python 3.10.0" appear in your terminal. 

For more info on install Python on your computer, see this link: https://www.tutorialspoint.com/how-to-install-python-in-windows. 

Once Python is installed, pip should also be installed. See this link for ways on how to check that pip is installed: https://pymotw.com/3/ensurepip/. 

### Getting started with flask
 
 #### See this link for installation: https://flask.palletsprojects.com/en/2.0.x/installation/

 For installing flask, first go into the directory: cs50finalproject (type cd cs50finalproject in terminal)

 #### Creating a virtual environment

 ##### Make sure you are in the cs50finalproject directory before doing the following steps

 Create a virtual environment via the terminal command: python3 -m venv venv 

 To activate the environment, type the command: . venv/bin/activate
 in your terminal (ensure that you are in the cs50finalproject directory)

 In the command-line of the terminal, you should see (.venv)

Once you activated the environment, type the following command to install Flask: $ pip install Flask. 

If this command does not work on your computer, try $ pip3 install Flask. 

##### Configuring Flask application - Link for info: https://flask.palletsprojects.com/en/2.0.x/quickstart/

The FLASK_APP environment variable lets the terminal know which application to run. We need to export this variable via the following command: export FLASK_APP=app.py.

Then run flask run and you should see a URL (http://127.0.0.1:5000/) to run the flask app

Next, specify that the environment we are running the Flask application is a development environment: 

Type $ export FLASK_ENV=development in terminal. 

Calling flask run again, you should see "Environment: development" in the terminal. 

It is advisable to run this project in debug mode (if testing the code), so the server automatically reloads if you change the code. Enable debug mode with the command: $ export FLASK_DEBUG=1.

###### Send Emails

To set up an email sender for this project, on line 543 and line 838 of app.py (sender=""), write an email address for the sender (it can be any email address; you might create a new email address to run this password). Set the username to the email in your on your os by typing the terminal command: export MAIL_USERNAME=''. To set the password for the email address on your os, please type the command: export MAIL_PASSWORD='' in your terminal. Between the quotation marks(''), type the relevant username and password for the email address you are using to run the project. 

##### Select Python Interpreter

Go the the Command Pallete by going to the top menu bar of VSCode and click View, which displays "Command Palette" under it. 

Click "Command Palette", and you should see an input field to type a command. Type "Python: Select Interpreter" or ">Python: Select Interpreter" (if the ">" doesn't show up automatically).

Out of the options, select "Python 3.10.64-but ('venv':venv)"

### Install Python Packages

#### App.py

Look at the top of app.py to see all the libraries used in that python file

###### Install CS50 library: https://cs50.readthedocs.io/libraries/cs50/python/

Install the CS50 library with the following command $ pip3 install cs50. Try pip install cs50 if the former does not work for your operating system. 

Next install flask session with the following command: $ pip install

###### Install Flask Session: https://pypi.org/project/Flask-Session/#description

Install Flask session with command: $ pip install Flask-Session

###### Install werkzeug: https://pypi.org/project/Werkzeug/

Install werkzeug with command: $ pip install Werkzeug.

##### Install flask_mail: https://pythonhosted.org/Flask-Mail/

Use the command: $ pip install Flask-Mail

##### Notes

errors, genres, helpers refer to other Python files, so you don't download them because they are not Python modules. 

os, app, and datetime are modules already included in the original installation of Python, so do not download them. 

#### errors.py

Go to the file errors.py

##### Install functools: https://pypi.org/project/functools/

Use this terminal command to install the functools library: $ pip install functools

If you followed the steps above, you do not need to install Flask. If you run $ pip install Flask in your terminal again, it should indicate "Requirement already satisfied" if 
flask is installed correctly. 

#### helpers.py

Go to the file helpers.py

##### Install regex

To access, the "re" module, type the following terminal command: $ pip install regex

### Other notes on Python Packages

Other than the ones listed above, there is no new Python packages used in genres.py, images.py, and manage.py except the csv module (which is built into Python)

### Running sqlite3

To run sqlite3, go to this link: https://www.sqlite.org/download.html, and download the precompiled binary file for your operating system. If you have a Mac, download the one for Mac, and if you have Windows, download the one for Windows. Then, you should type "which sqlite3" in the command-line, it should indicate where the files are located (ex. /usr/bin/sqlite3). 

One sqlite3 is installed, type "sqlit3 books.db" in the terminal, and then ".schema" to view the tables in the books.db file. 


### Loading data in SQL

In the terminal, make sure you are in the project directory (type $ cd cs50finalproject command-line to access directory)

Also, make sure the virtual environment is activated (to activate type venv/bin/activate
in command-line)

Then, run sqlite3 books.db, two tables: books and images should be preloaded with data from a csv file: books.csv. 

If you happen to not see any data from those two tables, you can load data into those tables by running manages.py and images.py.

manage.py loads the book information (from books.csv) into the books table while images loads images of the books cover into the images table. 

#### Note: You only need to run manages.py and images.py if you see no data in those two tables. 


### Install Fullcalendar.js and chart.js

This project uses two JavaScript libraries: Fullcalendar.js and Chart.js 

Link to FullCalendar.js: https://fullcalendar.io/docs/initialize-globals

Download FullCalendar.js by typing the following in the terminal command-line: npm install fullcalendar.

Link to Chart.js: https://www.chartjs.org/docs/latest/

Download Chart.js by typing the following in the command-line: npm i chart.js. 


### Defining upload path

For taking image input, the web app stores images in the uploads folder in the static directory. On line 39, you well see that the upload_folder path is defined as 
app.config["UPLOAD_FOLDER"] = "/Users/gersonpersonnat/cs50finalproject/static/uploads". You need to change the file path to take image input on your own OS. To do so, replace the file path above with the file path of the folder on your OS. You can find the path by going into the uploads directory (type cd cs50 final project then cd static then cd uploads). One you are in the uploads directory, type $ pwd in the command-line to get the full path. Replace "/Users/gersonpersonnat/cs50finalproject/static/uploads" with the path that appears in your terminal. 

### Running web app in server




Now that all the packages are installed, you can run the web app, via the command (flask run). 

To configure, note: 

Configure App: export FLASK_APP=app.py

Turn Debug Mode On: export FALSK_DEBUG=1

Set environment: FLASK_ENV=development

Set username for email address in os: export MAIL_USERNAME=''

Set password for email address in os: export MAIL_PASSWORD=''




