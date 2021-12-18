import csv
from cs50 import SQL



db = SQL("sqlite:///books.db")

# CSV File with books: https://www.kaggle.com/shashwatwork/best-book-ever-data-for-2021/version/1
books_file = open("books.csv", "r")

# Reads csv file with DictReader
books_dictionary = csv.DictReader(open("books.csv", "r"))

# Loads books into SQL Table books
for row in books_dictionary:
   db.execute("INSERT INTO books (title, author, genres, publish_date, description, pages) VALUES(?, ?, ?, ?, ?, ?)", row["title"], row["author"], row["genres"], row["publishDate"], row["description"], row["pages"])




    




