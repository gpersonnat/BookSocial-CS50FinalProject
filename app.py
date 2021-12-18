from cs50 import SQL
from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from errors import error, login_required
from genres import filter_genres, class_years, list_of_genres, find_matches_genres, find_matches_books, find_list_books
from helpers import convert_dict_to_list, check_email, dict_change_values
from werkzeug.utils import secure_filename
import os
import app
from flask_mail import Mail, Message
from datetime import date, datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError


# Configures app
app = Flask(__name__) 

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Configures flask_mail
# Requires that "Less secure app access" be on
# https://support.google.com/accounts/answer/6010255
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Only allow jpg, png, or gif files 
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".gif"]

# only allow files that are max 1b
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Store these uploads in uploads directory
app.config["UPLOAD_FOLDER"] = "/Users/gersonpersonnat/cs50finalproject/static/uploads"


# Configures session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """User can get info on book and displays recommmended list of books"""
    # Genres user selects
    if request.method == "POST":
        # Gets id of book that user requests info for
        book_id = request.form.get("book_id")
        # Finds info about book by querying into books table
        book_info = db.execute("SELECT books.id, books.title, books.author, books.publish_date, books.genres, books.description, images.image_link FROM books JOIN images on books.id = images.book_id WHERE books.id = ?", int(book_id))[0]
        # Displays html page showing info about that specific book
        return render_template("book_info.html", book_info=book_info)
    else:
        # Gets the genres the user selected when they created their profile
        genres = db.execute("SELECT genres FROM genres WHERE user_id = ?", session["user_id"])
        selected_genres = convert_dict_to_list(genres, "genres")
        # Get user's past 5 searches
        searches = convert_dict_to_list(db.execute("SELECT search FROM searches WHERE user_id = ? ORDER BY time_search DESC LIMIT 5", session["user_id"]), "search")
        # List of books based on past searches
        searches_list = tuple(find_list_books(searches))
        # Selects books based on genres user suggested / doesn't display books user is currently reading
        
        books = db.execute("SELECT DISTINCT books.id, books.title, books.author, images.image_link FROM books JOIN images ON books.id = images.book_id WHERE (books.id IN (?) OR(genres LIKE ? OR genres LIKE ? OR genres LIKE ?)) AND books.id NOT IN (SELECT book_id FROM collections WHERE user_id = ?) AND book_id NOT IN (SELECT book_id FROM removed_books WHERE user_id = ?) LIMIT 100", searches_list, "%" + selected_genres[0] + "%", "%" + selected_genres[1] + "%" , "%" + selected_genres[2] + "%", session["user_id"], session["user_id"])
        
        return render_template("index.html", books=books)

@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "POST":

        # Searchs books based on User's search
        books = db.execute("SELECT DISTINCT books.id, books.title, books.author, images.image_link FROM books JOIN images ON books.id = images.book_id WHERE title LIKE ? OR description LIKE ? OR author LIKE ? OR genres LIKE ?", "%" + str(request.form.get("search")) + "%", "%" + str(request.form.get("search")) + "%", "%" + str(request.form.get("search")) + "%", str(request.form.get("search")) + "%")
        # Checks if user inputed a sarch
        if not request.form.get("search"):
            return error("Please enter search result", "/search", 400)
        # Inserts that search into search results table
        db.execute("INSERT INTO searches (user_id, search) VALUES (?, ?)", session["user_id"], request.form.get("search"))
        # Shows search results
        return render_template("search.html", books=books, length=len(books))
    else:
        # For redirecting if there is an error and user goes back to index page
        return redirect("/")


@app.route("/search_profile", methods=["POST"])
@login_required
def search_profile():
    """User searches profile of other user"""

    search = request.form.get("search")
    # Searchs profiles by finding attributes similar to search
    profiles = db.execute("SELECT DISTINCT user_id, first_name, last_name, email, class_year FROM profiles JOIN users ON users.id = profiles.user_id WHERE (profiles.first_name LIKE ? OR profiles.last_name LIKE ? OR users.username LIKE ? OR profiles.class_year LIKE ?) AND profiles.user_id != ?", "%" + str(search) + "%", "%" + str(search) + "%", "%" + str(search) + "%", "%" + str(search) + "%", session["user_id"])

    # If user submitted a blank search result
    if not search: 
        return error("Please enter a search result", "/matches", 400)

    return render_template("profile_search.html", profiles=profiles, length=len(profiles))
    
    

@app.route("/login", methods = ["GET", "POST"])
def login():
    """Login users"""

    # Forget previous sessions
    session.clear()

    # If user submitted post method 
    if request.method == "POST":

        
        # Checks if username wasn't submitted
        if not request.form.get("username"):
            return error("Please enter username", "/login", 400)
        
        # Checks if password wasn't submitted
        if not request.form.get("password"):
            return error("Please enter password", "/login", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Makes sure username is correct and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return error("Username and/or password is not correct", "/login", 400)

        # Queries database to look for if user has created a profile
        profile = db.execute("SELECT * FROM profiles WHERE user_id = (SELECT id FROM users WHERE username = ?)", request.form.get("username"))
        
        # Checks if user has created profile
        if len(profile) == 0:
            # Assign session["user_id"] and brings user back to create_profile page
            session["user_id"] = rows[0]["id"]
            return render_template("create_profile.html", genres=filter_genres(), years=class_years())

        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
 
        #Redirects to home page
        return redirect("/")

        # If user submitted GET request
    else:
        return render_template("login.html")
        

@app.route("/register", methods = ["GET", "POST"])
def register():
    """Registers users"""
    if request.method == "POST":

        # Gets username from user input
        username = request.form.get("username")

        # Generates hash key for password that user inputs in
        hash = generate_password_hash(request.form.get("password"))

        # Checks if user doesn't input 
        if not request.form.get("username"):
            return error("Please enter username", "/register", 400)

        # Checks if username already exists 
        if len(db.execute("SELECT username FROM users WHERE username = ?", username)) != 0:
            return error("Username already exists", "/register", 400)

        # If user didn't input a password
        if not request.form.get("password"):
            return error("Please enter password", "/register", 400)

        # If confirmed password does not match password
        if request.form.get("confirmation") != request.form.get("password"):
            return error("Passwords do not match", "/register", 400)

        # Inserts user password into users table
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]
        
        # Redirects to Create_Profile   
        return redirect("/create_profile")
        
    # If users submitted GET request
    else:
        return render_template("register.html")

@app.route("/create_profile", methods = ["GET", "POST"])
@login_required
def create_profile():
    """User creates profile"""
    if request.method == "POST":

        # Checks if user inputs first name
        if not request.form.get("first_name"):
            return error("Please enter first_name", "/create_profile", 400)

        # Checks if user inputs last name 
        if not request.form.get("last_name"):
            return error("Please enter last name", "/create_profile", 400)

        # CHecks if user inputs email address
        if not request.form.get("email"):
            return error("Please enter email", "/create_profile", 400)

        # Checks if user inputs class year
        if not request.form.get("years"):
            return error("Please enter class year", "/create_profile", 400)

        # Checks if user selects genres
        if not request.form.get("genre1") or not request.form.get("genre2") or not request.form.get("genre3"):
            return error("Please select 3 genres", "/create_profile", 400)
        
        # Checks if user email is valid
        if not check_email(request.form.get("email")):
            return error("Please enter a valid emial address", "/create_profile", 400)
        
        # Put three genres into a list
        genres = [request.form.get("genre1"), request.form.get("genre2"), request.form.get("genre3")]

        # Checks if user has created profile on line
        if len(db.execute("SELECT * FROM profiles WHERE user_id = ?", session["user_id"])) !=0:
            return error("You already created a profile", "/", 400)
        
        # Used this source to learn how to allow user to upload file
        # https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
        
        # Takes uploaded file
        uploaded_file = request.files["file"]

        # If user does not upload a profile picture, sets user's profile picture to the default_profile.png
        if not request.files["file"]:
            filename = "default_profile.png"
        else: 
            # Gives uploaded filename a srecure filename
            filename = secure_filename(uploaded_file.filename)
            # Ensures that file has a valid extension (jpg, png, or gif)
            if os.path.splitext(filename)[1] not in app.config["UPLOAD_EXTENSIONS"]:
               return error("Please upload valid file", "/create_profile", 400)
            # Saves file to /static/uploads directory
            uploaded_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        
        # Inserts profile information into profile table
        db.execute("INSERT INTO profiles (user_id, first_name, last_name, email, bio, class_year, profile_image) VALUES (?, ?, ?, ?, ?, ?, ?)", session["user_id"], request.form.get("first_name"), request.form.get("last_name"), request.form.get("email"), request.form["message"], request.form.get("years"), filename) 

        # Inserts three genres into genres SQL table (which stores the genres that the user is interested in)
        for i in range(len(genres)):
            db.execute("INSERT INTO genres (user_id, genres) VALUES (?, ?)", session["user_id"], (genres)[i])

       
        return redirect("/")
    else:
        return render_template("create_profile.html", genres=filter_genres(), years=class_years())

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget user id
    session.clear()

    #Redirect user to login
    return redirect("/login")

@app.route("/profile")
@login_required
def profile():
    profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", session["user_id"])[0]
    return render_template("profile.html", profile=profile)

@app.route("/update_profile", methods = ["GET", "POST"])
@login_required
def update_profile():
   """User updates profile"""
   if request.method == "POST":

       # Checks if email address is a valid email address
       if not check_email(request.form.get("email")):
           return error("Please enter valid email address", "/update_profile", 400)
        
       # ALlows user to upload new profile pic
       uploaded_file = request.files["file"]

       bio = request.form["message"]
       # Checks if user didn't change bio
       if not request.form["message"]:
           bio = db.execute("SELECT bio FROM profiles WHERE user_id = ?", session["user_id"])[0]["bio"]


       # If user doesn't upload a profile picture, sets filename to orginal profile_image
       if not request.files["file"]:
           filename = db.execute("SELECT profile_image FROM profiles WHERE user_id = ?", session["user_id"])[0]["profile_image"]
       # If user uploads a new profile picture

       else:
            filename = secure_filename(uploaded_file.filename) 
            if os.path.splitext(filename)[1] not in app.config["UPLOAD_EXTENSIONS"]:
                return error("Please upload valid file", "/update_profile", 400)
            # Saves that profile picture to uploads folder
            uploaded_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
       # Updates user's profile details
       db.execute("UPDATE profiles SET first_name = ?, last_name = ?, email = ?, bio = ?, profile_image = ? WHERE user_id = ?", request.form.get("first_name"), request.form.get("last_name"), request.form.get("email"), bio, filename, session["user_id"]) 
       
       # Redirects user to profile page
       return redirect("/profile")
   
   # User clicks update profile
   else:
        profiles = db.execute("SELECT * FROM profiles WHERE user_id = ?", session["user_id"])[0]
        return render_template("update_profile.html", profile=profiles)
    
@app.route("/book_info", methods= ["POST"])
@login_required
def add_book():
    """ Adds book to user's collection table"""
    # Requests book's title, author, and id
    book_title = request.form.get("title")
    author = request.form.get("author")
    book_id = int(request.form.get("book_id"))
    
    # Current books in shelf
    current_books = convert_dict_to_list(db.execute("SELECT book_id FROM collections WHERE user_id = ?", session["user_id"]), "book_id")
    # Checks if user already has that book int heir shelf
    if book_id in current_books:
        return error(f"You already have {book_title} by {author} to your shelf.", "/book_info", 400)
    # Checks to see if user doesn't add book that is already on their shelf
    db.execute("INSERT INTO collections (user_id, book_id, author, genres, book_image, book_title) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], int(request.form.get("book_id")), author, request.form.get("genres"), request.form.get("image"), book_title)
    return render_template("shelved.html", title=book_title, author=author)


@app.route("/shelf", methods = ["GET", "POST"])
@login_required
def shelf():
    """ Displays user's books that they are currently reading and user can see progress"""

    # If user clicks one of the view buttons on the shelf
    if request.method == "POST":
        # Gets book_id of book
        book_id = request.form.get("book_id")

        # Querys user's progress on that books
        progress = db.execute("SELECT pages_read, progress_percentage FROM collections WHERE user_id = ? AND book_id = ?", session["user_id"], int(book_id))[0]

        # Looks up pages in book
        pages_in_book = db.execute("SELECT pages FROM books WHERE id = ?", book_id)[0]["pages"]

        # Looks up pages user has left in book 
        pages_left = pages_in_book - progress["pages_read"] 

        # Get log times and pages logged at those times and converts those list of dictionaries to a list of values 
        labels = convert_dict_to_list(db.execute("SELECT log_time FROM logs Where user_id = ? AND book_id = ?", session["user_id"], int(book_id)), "log_time")
        values = convert_dict_to_list(db.execute("SELECT pages_logged FROM logs Where user_id = ? AND book_id = ?", session["user_id"], int(book_id)), "pages_logged")

        # Renders progress.html
        return render_template("progress.html", progress=progress, book_id = int(book_id),  pages_left=pages_left, values=values, labels=labels)
    # Displays user's shelf
    else:
        books = db.execute("SELECT * FROM collections WHERE user_id = ?", session["user_id"])
        return render_template("shelf.html", books=books)

@app.route("/progress", methods = ["POST"])
@login_required
def progress_log_button():
    """User clicks on log button"""
    # Gets id of book that user wants to see progress on
    book_id = request.form.get("book_id")
    return render_template("log.html", book_id = book_id)

@app.route("/log", methods=["POST"])
@login_required
def progress():
    "User can log progress on book"
    # Gets id of book that user is logging progress on
    book_id = int(request.form.get("book_id"))


    # Looks up pages in book
    pages_in_book = db.execute("SELECT pages FROM books WHERE id = ?", book_id)[0]["pages"]

    # Looks up how many pages the user has read
    pages_read = db.execute("SELECT pages_read FROM collections WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)[0]["pages_read"] 

    # If the user has already finished the book, don't add more pages
    if pages_read >= pages_in_book:
        return error("You already finished reading the book", "/book_info", 400)
  
    if not request.form.get("pages").isdigit() or int(request.form.get("pages")) < 1 or int(request.form.get("pages")) > int(pages_in_book):
        return error("invalid number of pages", "/book_info", 400)
    
     # Logs pages added in logs table
    db.execute("INSERT INTO logs (user_id, book_id, pages_logged) VALUES (?, ?, ?)", session["user_id"], book_id, request.form.get("pages"))


    # Updates pages read 
    db.execute("UPDATE collections SET pages_read = ? WHERE user_id = ? AND book_id = ?", pages_read + int(request.form.get("pages")), session["user_id"], book_id)

    # Calculates new pages read after the user logs it in
    new_pages_read = db.execute("SELECT pages_read FROM collections WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)[0]["pages_read"]

      # If user has finshed reading book, set pages_read to pages_in book
    if new_pages_read >= pages_in_book: 
        pages_read = pages_in_book

    # Calcuales percentage of book user has read
    progress_percentage = round(new_pages_read / pages_in_book, 2)*100

    # Updates percentage of pages user has read in collections table
    db.execute("UPDATE collections SET progress_percentage = ? WHERE user_id = ? AND book_id = ?", progress_percentage, session["user_id"], book_id)

    
    # If user has finished reading book_progress percentage = 100%
    if int(db.execute("SELECT progress_percentage FROM collections WHERE user_id = ? and book_id = ?", session["user_id"], book_id)[0]["progress_percentage"]) == 100:
        return render_template("finished.html", book=db.execute("SELECT * FROM books WHERE id = ?", book_id)[0])

    # Gets info about the book (for which progress is being logged)
    info = db.execute("SELECT * FROM collections WHERE book_id = ?", int(book_id))[0]

    added_pages = request.form.get("pages")

    if not added_pages.isdigit():
        return error("please put in a positive integer", "/book_info", 400)


    if int(added_pages) < 1:
        return error("please put in a number greater than 1", "/book_info", 400)

    if int(added_pages) > int(pages_in_book):
        return error("invalid number of pages", "/book_info", 400)

    return render_template("logged.html", info=info, added_pages = int(added_pages))


 

@app.route("/remove_book", methods=["POST"])
@login_required
def remove_book():
    """Removes book from shelf"""

    # Gets book_id 
    book_id = int(request.form.get("book_id"))

    # Check if book is already removed
    if len(db.execute("SELECT * FROM collections WHERE book_id = ? and user_id = ?", book_id, session["user_id"])) == 0:
            return error("You already removed this book or book is not in shelf", "/shelf", 400)
    
    # Gets info about that book
    info = db.execute("SELECT * FROM collections WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)[0]


    # Deletes that book from collections table and shelf 
    db.execute("DELETE FROM collections WHERE user_id = ? AND book_id = ?", session["user_id"], book_id)

    # Inserts into table removed_books
    db.execute("INSERT INTO removed_books (user_id, book_id) VALUES (?, ?)", session["user_id"], book_id) 

    # Renders removed page
    return render_template("removed.html", book=info)

@app.route("/matches")
@login_required
def match():
    """Finds matches for user based on what books they're reading and genres"""

    # Books user is reading
    sql_books = db.execute("SELECT book_id FROM collections WHERE user_id = ?", session["user_id"])

    # Converts list of dictionaries into list of book ids
    books_list = convert_dict_to_list(sql_books, "book_id")

    # finds matches based on books
    matches_books = tuple(find_matches_books(books_list, session["user_id"]))
    

    # Genres of books user is reading
    sql_genres = db.execute("SELECT genres FROM collections WHERE user_id = ?", session["user_id"])

    # Get list of genres user is reading
    genres_list = list_of_genres(sql_genres)
    
    # Gets list of matches based on genres of books user is reading
    matches_genres = tuple(find_matches_genres(genres_list, session["user_id"]))


    # Searches matches info in profiles table
    matches = db.execute("SELECT DISTINCT user_id, first_name, last_name, email, class_year FROM profiles WHERE user_id IN (?) OR user_id IN (?)", matches_genres, matches_books)

    return render_template("matches.html", matches=matches)

@app.route("/match_info", methods=["POST"])
@login_required
def match_info():
    user_id = int(request.form.get("user_id"))
    match_info = db.execute("SELECT * FROM profiles WHERE user_id = ?", user_id)[0]
    shared_books = db.execute("SELECT collections.book_title AS title, images.image_link AS image FROM collections JOIN images ON collections.book_id = images.book_id WHERE collections.user_id = ? AND collections.book_id IN (SELECT book_id FROM collections WHERE user_id = ?)", user_id, session["user_id"])
    return render_template("match_info.html", match_info=match_info, shared_books=shared_books, len_shared_books=len(shared_books))

@app.route("/connect", methods=["POST"])
@login_required
def connect():
    """User sends friend request to other users"""

    # Get id of friend receiving request
    receiver_id = int(request.form.get("user_id"))
       
    # Check if user already submitted request to that user   
    if len(db.execute("SELECT * FROM requests WHERE sender_id = ? AND receiver_id = ? AND status = ?", session["user_id"], receiver_id, "SENT")) != 0:
        return error("Request already sent", "/matches", 400)

    # Checks if user is already friends with that person
    if len(db.execute("SELECT * FROM requests WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)) AND status = ?", session["user_id"], receiver_id, receiver_id, session["user_id"], "FRIENDS")) != 0:
        return error("You are already friends", "/matches", 400)

    # Inserts requests into requests table 
    db.execute("INSERT INTO requests (sender_id, receiver_id, status) VALUES (?, ?, ?)", session["user_id"], receiver_id, "SENT")

    # Gets receiver name and first name
    receiver = db.execute("SELECT first_name, last_name from profiles WHERE user_id = ?", receiver_id)[0]    

    # Notifies receiver by email that request was sent

    # Recipents first_name and last_name 
    recipient = db.execute("SELECT * FROM profiles WHERE user_id = ?", receiver_id)

    # Gets first name in last name of sender
    first_name = db.execute("SELECT first_name FROM profiles WHERE user_id = ? AND user_id IN (SELECT sender_id FROM requests WHERE receiver_id = ?)", session["user_id"], receiver_id)[0]["first_name"]
    last_name = db.execute("SELECT last_name FROM profiles WHERE user_id = ? AND user_id IN (SELECT sender_id FROM requests WHERE receiver_id = ?)", session["user_id"], receiver_id)[0]["last_name"]

    # Sends message to users
    msg = Message(f"{first_name} {last_name} has sent you a friend request", sender="", recipients=[recipient[0]["email"]])
    mail.send(msg)

    # Displays message that request is sent
    return render_template("sent.html", receiver = receiver)

@app.route("/requests")
@login_required
def requests():
    """Shows user's sent requests"""
    requests = db.execute("SELECT * FROM requests JOIN profiles ON requests.sender_id = profiles.user_id WHERE receiver_id = ? AND status = ? ORDER BY time_of_request DESC", session["user_id"], "SENT")
    return render_template("requests.html", requests=requests)


@app.route("/accept", methods=["POST"])
@login_required
def accept():
    """User accepts friend request"""
    
    # Gets id of user who sent request
    sender_id = int(request.form.get("sender_id"))

    # Updates status to accepted
    db.execute("UPDATE requests SET status = ? WHERE sender_id = ? AND receiver_id = ?", "ACCEPTED", sender_id, session["user_id"])
    requests = db.execute("SELECT * FROM requests JOIN profiles ON requests.sender_id = profiles.user_id WHERE receiver_id = ? AND (status = ? OR status = ?) ORDER BY time_of_request DESC LIMIT ?", session["user_id"], "ACCEPTED", "SENT", int(request.form.get("requests_length")))

    # Stores new request into table indicated that the two user's are friends
    db.execute("INSERT INTO requests (sender_id, receiver_id, status) VALUES (?, ?, ?)", sender_id, session["user_id"], "FRIENDS")
    
    # Stays on the same page without refreshing
    return render_template("requests.html", requests=requests)

@app.route("/friends")
@login_required
def friends():
    """Displays user's friends"""
    # Selects friends from requests table
    friends = db.execute(
        "SELECT * FROM profiles WHERE user_id IN (SELECT receiver_id FROM requests WHERE sender_id = ? AND status = ?) OR user_id IN (SELECT sender_id FROM requests WHERE receiver_id = ? AND status = ?)", session["user_id"], "FRIENDS", session["user_id"], "FRIENDS")
    return render_template("friends.html", friends=friends)
   
@app.route("/friend_info", methods=["POST"])
@login_required
def friend_info():
    """Displays books friend is reading"""
    # Gets books friends is reading
    books = db.execute("SELECT * FROM collections JOIN images on images.book_id = collections.book_id WHERE collections.user_id = ?", int(request.form.get("friend_id")))
    # Gets friend id from profiles
    friend = db.execute("SELECT * FROM profiles WHERE user_id = ?", int(request.form.get("friend_id")))[0]
    return render_template("friend_info.html", books=books, friend=friend)

@app.route("/friend_progress", methods=["POST"])
@login_required
def friend_progress():
    """ Displays friend's progress on a book"""
    # If user clicks progress next to book user is reading
    
    # Gets book_id of book
    book_id = int(request.form.get("book_id"))

    # Gets id of friend
    friend_id = int(request.form.get("friend_id"))

    # Querys friend's progress on that book
    progress = db.execute("SELECT pages_read, progress_percentage FROM collections WHERE user_id = ? AND book_id = ?", friend_id, book_id)[0]
    print(progress)

        # Looks up pages in book
    pages_in_book = db.execute("SELECT pages FROM books WHERE id = ?", book_id)[0]["pages"]

        # Looks up pages friend has left in book 
    pages_left = pages_in_book - progress["pages_read"] 

        # Get log times and pages logged at those times and converts those list of dictionaries to a list of values 
    labels = convert_dict_to_list(db.execute("SELECT log_time FROM logs WHERE user_id = ? AND book_id = ?", friend_id, book_id), "log_time")
    values = convert_dict_to_list(db.execute("SELECT pages_logged FROM logs WHERE user_id = ? AND book_id = ?", friend_id, book_id), "pages_logged")

    # Display's friend's progress on book
    return render_template("friend_progress.html", progress=progress,  pages_left=pages_left, values=values, labels=labels)
    


@app.route("/unfriend", methods=["POST"])
@login_required
def unfriend():
    """Unfriend immediately after accepting request"""
    # Get id of friend (person who sent the request)
    friend_id = int(request.form.get("sender_id"))
    db.execute("DELETE FROM requests WHERE sender_id = ? AND receiver_id = ?", friend_id, session["user_id"])

    # Gets friend's name
    friend_name = db.execute("SELECT first_name, last_name FROM profiles WHERE user_id = ?", friend_id)

    return render_template("unfriended.html", friend=friend_name[0])

@app.route("/remove_friend", methods=["POST"])
@login_required
def remove_friend():
    "Remove friend"
    
    # Get id of friend
    friend_id = int(request.form.get("friend_id"))
    
    # Remove from requests table
    db.execute("DELETE FROM requests WHERE (sender_id = ? AND receiver_id = ?) OR (receiver_id = ? AND sender_id = ?)", friend_id, session["user_id"], friend_id, session["user_id"])

    # Gets friend's name
    friend_name = db.execute("SELECT first_name, last_name FROM profiles WHERE user_id = ?", friend_id)
    
    # Displays message that user removed the other user as a friend
    return render_template("unfriended.html", friend=friend_name[0])



@app.route("/events", methods=["GET", "POST"])
@login_required
def events():
    """Display events"""
    # Get events 
    if request.method == "POST":
        return redirect("/event_info")
    else:
        # Gets list of user's friends (by converting a SQL_Query into a list of friend ids)
        friends = convert_dict_to_list(db.execute("SELECT sender_id FROM requests WHERE receiver_id = ? AND status = ? UNION SELECT receiver_id FROM requests WHERE sender_id = ? AND status = ?", session["user_id"], "FRIENDS", session["user_id"], "FRIENDS"), "sender_id")

        # Queries events user is attending
        attending_events = db.execute("SELECT * FROM events WHERE id IN (SELECT event_id FROM attendees WHERE attendee_id = ?)", session["user_id"])

        # Queries events that friends are hosting
        friend_events = db.execute("SELECT DISTINCT id, creator_id, title, date, start_time, end_time FROM events WHERE events.creator_id IN (?) AND id NOT IN (SELECT event_id FROM attendees WHERE attendee_id = ?) ORDER BY date, start_time", tuple(friends), session["user_id"])

        # Renders events.html
        return render_template("events.html", attending_events=attending_events, friend_events=friend_events, today_date=str(date.today()))


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        # Gets events, date, and time, and description from form
        event_title = request.form.get("event_title")
        event_date = request.form.get("date")
        start_time = request.form.get("time")
        end_time = request.form.get("end_time")
        description = request.form["message"]

        # Checks if user put title
        if not event_title:
            return error("Please enter title for event", "/post", 400)

        # Checks if user put date, time, and, event_time
        if not event_date:
            return error("Please enter date", "/post", 400)
        if not start_time: 
            return error("Please enter start time", "/post", 400)
        if not end_time:
            return error("Please enter end time", "/post", 400) 

        # Check if end time comes after start_time
        if start_time >= end_time:
            return error("Please enter valid end time", "/post", 400)

         # Takes uploaded file
        uploaded_file = request.files["file"]

        # Checks if user inputted image
        if not request.files["file"]:
            filename = "default_event.png"
        else: 
            filename = secure_filename(uploaded_file.filename)
            if os.path.splitext(filename)[1] not in app.config["UPLOAD_EXTENSIONS"]:
               return error("Please upload valid file", "/post", 400)
            uploaded_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
               
        # INSERT into events table
        db.execute("INSERT INTO events (title, creator_id, date, start_time, end_time, event_image, description) VALUES (?, ?, ?, ?, ?, ?, ?)", event_title, session["user_id"], event_date, start_time, end_time, filename, description)

        # Get id of event just posted
        event_id = db.execute("SELECT id FROM events WHERE creator_id = ? ORDER BY event_posted_time DESC LIMIT 1", session["user_id"])[0]["id"]

        # Makes event creator is an attendee
        db.execute("INSERT INTO attendees (event_id, attendee_id) VALUES (?, ?)", event_id, session["user_id"])
        
        # Redirects back to events page
        return redirect("/events")
    else:
        today_date = str(date.today())
        return render_template("post.html", today_date=today_date)
    
@app.route("/event_info")
@login_required
def event_info():
    """Shows events"""
    attending_events = dict_change_values(db.execute("SELECT * FROM events WHERE id IN (SELECT event_id FROM attendees WHERE attendee_id = ?) ORDER by date, start_time", session["user_id"]), ["start_time", "end_time"])
    # Gets friends events
    
    # Queries users friends and converts into into a list
    friends = convert_dict_to_list(db.execute("SELECT sender_id FROM requests WHERE receiver_id = ? AND status = ? UNION SELECT receiver_id FROM requests WHERE sender_id = ? AND status = ?", session["user_id"], "FRIENDS", session["user_id"], "FRIENDS"), "sender_id")
    
    # In New events, displays events that friends are hosting
    friend_events = dict_change_values(db.execute("SELECT DISTINCT id, creator_id, title, date, start_time, end_time FROM events WHERE events.creator_id IN (?) AND id NOT IN (SELECT event_id FROM attendees WHERE attendee_id = ?) ORDER BY date, start_time", tuple(friends), session["user_id"]), ["start_time", "end_time"])


    return render_template("events_page.html", attending_events=attending_events, friend_events=friend_events)

@app.route("/signup", methods=["POST"])
@login_required
def signup():
    """User signs up for event"""
    event_id = request.form.get("event_id")
    db.execute("INSERT INTO attendees (event_id, attendee_id) VALUES (?, ?)", event_id, session["user_id"])
    return redirect("/event_info")


@app.route("/meeting_info", methods=["POST"])
@login_required
def meeting_info():
    """Displays event info"""
    
    # Gets id of event that user wants to get info on
    event_id = int(request.form.get("event_id"))
   
    # Gets id of person who created the event
    creator_id = int(request.form.get("creator_id"))
   
    # Gets meeting info and formats the time
    meeting = dict_change_values(db.execute("SELECT events.id, events.title, events.creator_id, events.start_time, events.end_time, events.date, events.event_image, events.description, profiles.first_name, profiles.last_name FROM events JOIN profiles ON profiles.user_id = events.creator_id WHERE events.id = ? AND events.creator_id = ?", event_id, creator_id), ["start_time", "end_time"])[0]

    # View where user doesn't see attendees
    see_attendee_list = "false"

    return render_template("meeting_info.html", meeting=meeting, see_attendee_list=see_attendee_list)

@app.route("/see_attendees", methods=["POST"])
@login_required
def see_attendees():
    
    # Gets id of event user wants to see attendees for 
    event_id = int(request.form.get("event_id"))
    
    # Finds attendees for that event
    attendees = db.execute("SELECT first_name, last_name, profile_image FROM profiles WHERE user_id != ? AND user_id IN (SELECT attendee_id FROM attendees WHERE event_id = ?)", session["user_id"], event_id)

    # Info about that event 
    creator_id = int(request.form.get("creator_id"))
    
    # Reformats the time from 24-hour to 12-hour format using dict_change_values
    meeting = dict_change_values(db.execute("SELECT events.id, events.title, events.creator_id, events.start_time, events.end_time, events.date, events.event_image, events.description, profiles.first_name, profiles.last_name FROM events JOIN profiles ON profiles.user_id = events.creator_id WHERE events.id = ? AND events.creator_id = ?", event_id, creator_id), ["start_time", "end_time"])[0]
    
    # Lets route know that user is seeing attendees
    see_attendee_list = "true"

    return render_template("meeting_info.html", meeting=meeting, attendees=attendees, see_attende_list=see_attendee_list)


@app.route("/decline", methods=["POST"])
@login_required
def decline():
    """User declines event (after signing up)"""

    # Gets event_id 
    event_id = int(request.form.get("event_id"))
    # Delete that user as attendee
    db.execute("DELETE FROM attendees WHERE event_id = ? AND attendee_id = ?", event_id, session["user_id"])
    # Redirects to events page
    return redirect("/event_info")

@app.route("/cancel_button", methods=["POST"])
def cancel_button():
    """Takes user to form to cancel event"""
    return render_template("cancel.html", event_id = request.form.get("event_id"))

@app.route("/cancel", methods=["GET", "POST"])
def cancel():
    """User cancels event"""
    if request.method == "POST":
        # Gets cancellation message from user
        message = request.form["message"]
        event_id = int(request.form.get("event_id"))

        # Check if event has already been cancelled
        if len(db.execute("SELECT * FROM events WHERE id = ?", event_id)) == 0:
            return error("You already cancelled this event or event doesn't exist", "/events", 400)

        # Details of event being cancelled
        event = dict_change_values(db.execute("SELECT events.title, events.date, events.start_time, events.end_time, profiles.first_name, profiles.last_name FROM events JOIN profiles On events.creator_id = profiles.user_id WHERE events.id = ?", event_id), ["start_time", "end_time"])[0]


        # Recipients (attendees who signed_up)
        receivers = db.execute("SELECT email FROM profiles JOIN attendees ON attendees.attendee_id = profiles.user_id WHERE attendees.event_id = ? AND attendees.attendee_id != ?", event_id, session["user_id"])
    
        # Sends message to recipients
        with mail.connect() as conn:
            for receiver in receivers:
                msg = Message("One of your events has been cancelled",
                    sender="",
                    recipients=[receiver["email"]])
                msg.html = render_template("cancel_message.html", event=event, message=message)
                conn.send(msg)

        # Cancel event in delete from event and attendees table
        db.execute("DELETE FROM events WHERE id = ?", event_id)
        db.execute("DELETE FROM attendees WHERE event_id = ?", event_id)
    
        return render_template("cancelled.html")
    else: 
        return redirect("/events")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
