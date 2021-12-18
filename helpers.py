from cs50 import SQL, get_string
import re



db = SQL("sqlite:///books.db")




def convert_time(time):
    """Converts time from 24-hour format to 12-hour format"""
    # If time is between: 1:00 A.M and 9:59 AM
    if int(time[:2]) >=1 and int(time[:2]) <= 9:
        return(time.replace("0", "")+" AM")
    # If time is between: 10:00 AM and 11:59 AM
    if int(time[:2]) >= 10 and int(time[:2]) <= 11:
        return(time+" AM")
    # If time is between: 12:00 PM and 12:59 PM
    if int(time[:2]) == 12:
        return (time+ " PM")
    # If time is between 1:00 PM and 11:59 PM
    if int(time[:2]) >= 12 and int(time[:2]) <= 23:
        return(str(int(time[:2])% 12)+":"+time[-2:]+" PM")
    # If time is between 12:00 AM and 12:59 A.M
    if int(time[:2]) == 0:
        return(time.replace("00", "12")+" AM")


# Changes values in a dictionary list
def dict_change_values(sql_list, keys):
    """Changes values associated with time in a events table so we can format time in 12-hour format"""
    for row in sql_list:
        for key in keys:
            row[key] = convert_time(row[key])
    return sql_list
    
def convert_dict_to_list(sql_list, i):
    """Converts list of dictionaries to list of values"""
    list = []
    # For each dictionary in the list, add a the value assigned with a key to the list 
    for row in sql_list:
        list.append(row[i])
    # Returns the list
    return list


# Checks user's email
def check_email(email):
   """Checks if email is valid using regular expression"""
   # Used this source for email regular expression that determines whether email is valid or not: https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
   
   # Regex that checks validity of email addresss
   regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
   
   # Checks if email is valid
   if(re.fullmatch(regex, email)):
        return True
   else:
        return False