import csv
from cs50 import SQL


# Dictionary with Book Images

db = SQL("sqlite:///books.db")


# Reads images from books.csv
images_file = open("books.csv", "r")
images_dictionary = csv.DictReader(open("books.csv", "r"))



# Loads csv file into SQL Table images
for row in images_dictionary:
    book_id = db.execute("SELECT id FROM books WHERE title = ? AND author = ? AND publish_date = ?", row["title"], row["author"], row["publishDate"])[0]["id"]
    db.execute("INSERT INTO images (book_id, image_link) VALUES (?, ?)", book_id, row["coverImg"])

