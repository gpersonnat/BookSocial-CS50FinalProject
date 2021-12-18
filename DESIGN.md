# Design Document

## Name 

Gerson Personnat

## Project Title

BookSocial

### Introduction

This web app allows a user to create a profile, find books that they are interested in reading, track progress on those books, and connect with other users on the app. The app overall works from requesting form data, passing data into a Flask app, and then storing that data into a SQL database: books.db. This project uses Flask and Python for backend development; HTML, CSS, and JavaScript for front-end development; and Jinja as a templating engine to render HTML pages. 

### Structure

The project directory contains the configuration files: pycache and .venv file for configuration. The static folder stores the static files: the styles.css, our default images (for profile and events), and an uploads folder with the images that the user uploads. The templates folder stores our HTML files. app.py is the main Python file where we run the app and genres.py, errors.py, helpers.py, and images.py, and manage.py are supporting Python files. genres.py. errors.py, and helpers.py contain "helper" functions and variables that we use in app.py. I decided to use genres.py, errors.py, and helpers.py to abstract technical programs such as manipulating data types (i.e., converting a list of dictionaries to a list with values), validating (i.e., checking if an email is valid), and formatting data (i.e. converting a data from a 24-hour format to a 12-hour format). 

The data I used for the books is from this source: https://www.kaggle.com/shashwatwork/best-book-ever-data-for-2021/version/1. I choose this data because it was a free option that had an adequate amount of book data (including fields such as description, book cover image). For a longer-term project, I would likely use the Google Books API; however, for this project, given the time of development, I decided to use a CSV file and load it into a SQL data table. 

manage.py and images.py load book data into a SQL table; they read data from books.csv, and for each row in the CSV file, insert that row data into the SQL tables books and images, respectively. To load the data into the table, I ran python manage.py and images.py in the terminal. 

### Program

#### app.py

##### Register

The register feature is implemented via the "/register" route. In register.html, a form takes three fields: username, password, and password confirmation and submits a "POST" request to "/register". It handles errors such as checking whether the user inputs a username, password, or confirmed password and whether the username already exists. Then we insert a user's username and a hash of the password (via generate_password_hash) into the users table. Then, the register() redirects to "/create_profile", where the user creates their profile.

##### Create Profile

create_profile() allows the user to create a profile where they fill out their first name, last name, email address, three genres that they would like to read, and a profile picture. The first three fields are required while the profile picture is optional (if the user does not submit a profile picture), the filename is set to "default_profile.png", which is in the static folder. The user's uploaded file is saved in the /static/uploads directory. 

To take the three selected genres, I used three separate dropdown boxes. Originally, I used an HTML multi-select form field, but it did not seem user-friendly. I looked up multi-select libraries and templates online, but configuring those libraries required more research for a small detail of the project. In further developing this project past the deadline, I would try to do more research in implementing a user-friendly multi-select form. 

Another thing to note in create_profile.html is that I did not extend my "layout.html" (which provides a layout for other templates) using Jinja. create_profile.html is the only HTML page that I did not extend layout.html to account for the case of if the user clicked out of "/create_profile" or logged out. If the user does not finish creating their profile page, the next time they log in, it will redirect them back to create_profile. 

create_profile then inserts data into the SQL table "profiles" and inserts the three selected genres into the "genres" table. 

###### Helper Functions (create_profile())

I used one helper function (check_email()) in helpers.py that checks whether an email address is a valid email address, using a regular expression used by this source: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/. 

##### Dashboard (index)

index(), if the request method is a "GET" method, displays the recommended list of books based on the an algorithim that finds books related to the user's three selected genres and the user's last 5 searches when they search for a "book." Given the time constraints, I used a simpler book matching algorithm, but in further developing this algorithm, I would do more research into basic machine learning models that I could implement. I also limited the search results to 5 for the sake of run time, but I would be able to use user's search history to generate a recommended list of books by researching more complex models. If the request method is "POST," the server renders a page that displays information about a book the user selected by clicking "Info". 

To design this, I needed to know what book was selected, so I was deciding which method would be best to pass data from the frontend to the backend. Passing from backend to frontend was simpler in I could use Jinja. Another method that I thought of was using JavaScript to listen for when a user clicks a button, set the id attribute of each book in the table the book_id, and retrieve that book_id via document.getElementById, and then send that to the flask route via a POST request. However, in using AJAX to post data to Flask, I did not have access to render_template because AJAX does not directly post to the browser. 

Thus, I effectively decided to wrap a form tag around the "Info" buttons in HTML, set an input type field that stored the value of the book_id, and then use request.form.get("book_id") to get the value of the book_id. This approach involves adequate design because book_id is not confidential information, so it is okay for the user to see these ids in the page source. In fact, this approach seems to be more efficient than posting data via AJAX because we do not need to work around not having access to render template or redirect. For other similar cases on my website, I use this approach, where there are multiple items in a list or row in a table, and there is a button associated with them. I would not consider data like user_id to be confidential, because it is simply a SQL table identifier used on the backend, and the clients do not have access to the backend, so they could not do anything with using user_id. 

##### Shelf and Progress

The shelf displays the books that the user has added to their collection, and shelf.html is displayed when the user submits a "GET" request. A user submits a "POST" request when they click the view button, and that request renders progress.html, which allows them to view the progress on their book. 

For the chart, I used the line chart in Chart.js (source: https://www.chartjs.org/docs/latest/charts/line.html). Since this feature is only one of the features in my project, for time purposes, I used a line chart that displays the time stamp that the user logged the number of pages read on the x-axis, and the pages read on the y-axis. However, in further developing this project, I would add other types of charts, such as scatter plots and pie graphs, that display different types of data. In the "progress" SQL table, I track the books that the user is reading, and the progress (pages read and percentage of pages read for each book). I would also allow users to see progress by days, weeks, and months, but that would also involve querying data from the SQL table and formatting TIMESTAMP to see what the user logged on that day. These implementations would not be more difficult, but they would be more time-consuming, but since there are other more prominent features for this web app, I included a line chart as a foundation for further development of this feature. 

Based on the Chart.js documentation, where labels are the x-axis values and data is the y-axis values, I needed to store the log times and pages logged in two lists and under the script tags in prgoress.html pass those lists in the labels JavaScript array and the data property of the data object. To serialize the Python data, I used "tojson" Jinja attribute. In events.html, when I use FullCalendar.js, I take a similar approach passing in Python variables to JavaScript to Jinja. 

When passing Jinja into JavaScript (inside the script tags), we do see error messages appear (shown in problems of CLI) but passing Jinja into JavaScript is valid. I think that this is the more concise and efficient approach than storing the data in HTML and parsing HTML tags with JavaScript; however, in further developing the project and considering deploying it in a production environment, I would probably adopt another approach to ensure that the code is secure. 

###### Helper Functions (shelf())

For shelf, I use a custom-made function called convert_dict_to list which converts a list of dictionaries (a SQL query) into a list of values. I defined the function in the helpers.py file because it allowed me to abstract away data type manipulation from my main app.py file. This function takes in as argument the list of dictionaries and a key, and appends the values associated with the key for each dictionary in the list into a new list. 

### Connect and Matches

Connect allows users to connect with other users on the app. When a user submits a "GET" request to "/match" by clicking "Connect" in the navbar, match() renders matches.html, which displays other users that the user has matched with based on the books they're reading and the genres that they're reading. 

To get the books the user is reading, we query the collections in books.db where the user_id is equal to the session["user_id"], the user_id of the current user, and store that SQL query in the variable sql_books. We do the same to get the genres of the books the user is reading, and store that in a variable sql_genres. We then use convert_dict_to_list to convert sql_books and sql_genres to lists and then pass them as arguments into find_matches_books and find_matches_genres, respectively. 

Although find_matches_books and find_matches_genres are repetitive, they differ than that the select queries are slightly different; for example, find_matches_books uses a LIKE operator. While, with more time, I would optimize design in this case, I did not optimize design because it is a small technicality for the scope of this project. 

### Requests and Friends

To create a connections system, where users can send and accept friend requests from other uses, I stored data in a SQL table called requests, with the status column indicating whether a request has been "SENT" or "ACCEPTED, or two users are "FRIENDS". I did not create a separate table for the "FRIENDS" status because, in the Requests Page, I wanted to create the effect that the user can accept multiple requests at a time without reloading the page and unfriend immediately after accepting a request. Also, it was not necessary, and possibly less efficient, to create another table storing the information of whether two users are friends. 

To create this effect, I made two separate routes for unfriending other users: "/unfriend", where a user removes a friend immediately after accepting a request, and "remove_friend" where a user removes a friend after reloading the page. After the user reloads the page, or clicks out of the Requests tab, the page does not show any past accepted requests. However, if the user accepts a request, and then accepts another request, then the page does not reload. In requests.html, I also keep track of the number of requests displayed on the page as a hidden form field using {{ requests|length }} to track the number of requests already displayed on the page. In "/accept," when a user accepts a request, when querying the past requests, I take all the requests that were previously displayed on the page (without refreshing) by ordering the SQL query requests by time_of_request and then limiting the query to the number of requests displayed (without the page reloaded). 

While this spec might be implemented with JavaScript, it would require me passing data from JavaScript to Flask to know which friend request was accepting. Therefore, I would probably have to use an Ajax post, which limits access to the render_template and redirect functions. Since this is a fast web development project, and it was quite clear how to implement this using Flask and Jinja, I stuck with that approach. However, in further developing project, I would look in to see if using JavaScript is more optimal and efficient in generating this effect than Flask and Jinja. 

### Events and Posts

For the route "/events", submitting a "POST" requesting by clicking "View" brings the user to the events page that shows their friends' events (under New Events) and Upcoming events that they have signed for. A get request displays events on a calendar, which I used the FullCalendar.js library: https://fullcalendar.io/docs/initialize-globals. Per the documentation, events displays a list of event objects that display on the graph. To define an event object, I stored a SQL query of the events (attending events and friends' events) in passed that SQL query into events.html via return render_template. Looking at events.html, I used a jinja for loop to define event objects. Clicking the "Post" button ("GET" request) brings the user to post.html, where the fill out a form to post an event. To reformat the date of the event in the events format from a 24-hour format to 12-hour format I used the custom-made function dict_change_values, which changes values associated with the start_date and end_date in the dictionaries. To reformat the dates in helpers.py, I created a custom-made convert_time() function. It was necessary to custom make the convert_time function because there was not a function in an easily accessible Python library that converts a string 24-hour time to a string 12-hour time. 

In events_page.html, the user can view info about the event by clicking the info page, and it renders the html file "meeting_info.html". So that the user can see the attendees (by clicking "Attendees"), without refreshing the page, I used a similar idea to the requests by creating a route called "/see_attendees" which renders meeting_info.html with a list of attendees on the side. 

### Conclusion

Overall, I was able to create a functional Flask application that generates a recommended list of books for users and allows users to connect with other book readers. Initially, I was planning to implement a book auction and exchange system and a coupon tracker that helps users by good deals for books. While I decided not to implement these to improve the functionality of more fundamental parts of the project, I would be able to implement these using the same design principles I used in this version of the project. There is potential for many more features in further development, but this version of the project provides all the essential functionalities in my initial vision of the project. 

