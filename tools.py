import sqlite3
from flask import redirect,session
from functools import wraps

#extract the sql query to a dictionary
def extract(query):
    dict_list = []
    try:
        for data in query:
            dict_list.append(dict(data))
    except:
        return dict_list
    return dict_list

# check if the user owns the table
def checker(TableID, UserID):
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    checker = []
    if UserID == None:
        checker = extract(db.execute("SELECT * FROM tables WHERE TableID = ? AND IsPublic = 1",(TableID,)).fetchall())
    else:
        checker = extract(db.execute("SELECT * FROM tables WHERE TableID = ? AND OwnerID = ?",(TableID,UserID)).fetchall())
    return checker

# Check if the password is valid
def pass_validate(password,confirmation):
    if not password == confirmation:
            return "Passwords do not match"
    if len(password) < 8:
            return "Password must be 8 characters or longer"
    if not any(char.isdigit() for char in password):
            return "Password must contain numbers"
    if not any(char.isalpha() for char in password):
            return "Password must contain letters"
    else:
         return "Valid"
    
# requires the user to login 
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function




