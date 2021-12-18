from cs50 import SQL
from helpers import convert_dict_to_list

db = SQL("sqlite:///books.db")

genres = db.execute("SELECT genres FROM books")



# https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/




# Filteres list of genres

def filter_genres():
     """Filters total list of genres for book"""
     combined_list = []
     # In books.csv, genres are formatted as a string; this reformats all the genres; this generates a list of the lists of genres in each book
     for i in range(len(genres)):
          combined_list.append(genres[i]["genres"].strip("[").strip("]").replace("'","").replace(", ", ",").split(","))


     # Used this source for learning how to remove duplicates from list via list comprehension: https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/

     # Formats the list, so it is just a list of all individual genres listed in the csv file
     combined_list = [x for l in combined_list for x in l]
     

     filtered_list = []
     # Removes duplicates from filtered"list with list comprehension
     [filtered_list.append(x) for x in combined_list if x not in filtered_list]
     return filtered_list




def list_of_genres(genres_sql):
     """Gets list of genres of booksuser is reading"""
     list = []
     for row in genres_sql:
          list.append(row["genres"].strip("[").strip("]").replace("'","").replace(", ", ",").split(","))
     # Same idea from filter_genres, convert a list of lists into a list of individual genres
     list = [d for s in list for d in s]
     filter_list = []
     # Remove duplicates from the list
     [filter_list.append(d) for d in list if d not in filter_list]
     return filter_list

# Find matches based on genres
def find_matches_genres(list_of_genres, session_user_id):
     """Finds other users reading a book with the saem genre"""
     matches = []
     # For each genre, finds matches reading the same genre
     for genre in list_of_genres:
          match = db.execute("SELECT DISTINCT user_id, first_name, last_name, email, class_year FROM profiles WHERE user_id != ? AND user_id IN (SELECT user_id FROM collections WHERE genres LIKE ?) AND user_id NOT IN (SELECT receiver_id FROM requests WHERE sender_id = ?) AND user_id NOT IN (SELECT sender_id FROM requests WHERE receiver_id = ?)", 
          session_user_id, "%" + genre + "%", session_user_id, session_user_id
          )
          matches_list = convert_dict_to_list(match, "user_id")
          matches += matches_list
     return matches

# Find matches based on books
def find_matches_books(list_of_books, session_user_id):
     """Finds other uses reading the same book"""
     matches = []
     # For each book fidn matches reading the same book
     for book in list_of_books:
          match = db.execute("SELECT DISTINCT user_id, first_name, last_name, email, class_year FROM profiles WHERE user_id != ? AND user_id IN (SELECT user_id FROM collections WHERE book_id = ?) AND user_id NOT IN (SELECT receiver_id FROM requests WHERE sender_id = ?) AND user_id NOT IN (SELECT sender_id FROM requests WHERE receiver_id = ?)", 
          session_user_id, book, session_user_id, session_user_id
          )
          matches_list = convert_dict_to_list(match, "user_id")
          matches += matches_list
     return matches

def find_list_books(list_of_searches):
     """Finds list of recommended books based on past user searches"""
     books = []
     # For each search (the previous 5 searches) finds books that have attributes similar to that search results
     for search in list_of_searches:
          book = db.execute("SELECT DISTINCT id FROM books WHERE title LIKE ? OR description LIKE ? OR genres LIKE ?", "%" + search + "%", "%" + search + "%", "%" + search + "%")
          book_list = convert_dict_to_list(book, "id")
          books += book_list
     return books


def class_years():
     """Stores list of class years"""
     return ["2022", "2023", "2024", "2025", "2026", "2027"]
 

