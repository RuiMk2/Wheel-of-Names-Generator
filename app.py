from http.client import REQUEST_ENTITY_TOO_LARGE
import sqlite3

from tools import extract,login_required,pass_validate,checker
from flask import Flask,redirect,render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Open the database
db = sqlite3.connect("database.db", check_same_thread = False)
# To allow the database to return data as list dictionaries
db.row_factory = sqlite3.Row

## Main Menu ##
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    tablesOwned = extract(db.execute("SELECT * FROM tables WHERE OwnerID = ? ORDER BY TableID DESC", (session["user_id"],)).fetchall())
    return render_template("index.html", user=session , choices=tablesOwned)


## Account Management ##
# Register new account
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("repassword")
        # query to check if username exists
        query = extract(db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall())
        # check if username is valid 
        if not username or not password or not confirmation:
            error = "Some fields are blank"
        elif not len(query) == 0:
            error = "Username already exists"
        elif not pass_validate(password,confirmation)== "Valid":
            error = pass_validate(password,confirmation)
        else:
            password = generate_password_hash(password)
            db.execute("INSERT INTO users(username, password) VALUES(?,?)", (username,password))
            db.commit()
            return render_template("login.html", status="Registration Success!")
        return render_template("register.html", status=error)
    return render_template("register.html")

# Login to an existing account
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(password)
        # query to compare credentials with
        query = extract(db.execute("SELECT * FROM users where username = ?", (username,)).fetchall())
        if not username or not password:
            error = "Some fields are blank"
        elif len(query) == 0:
            error = "Username does not exist"
        elif check_password_hash(query[0]["password"], password) == False:
            error = "Incorrect Password"
        else:
            # Saved to session if success
            session["user_id"] = query[0]["id"]
            session["username"] = query[0]["username"]
            return redirect("/")
        return render_template("login.html", status=error)
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
        session.clear()
        return redirect("/login")

# Change Password
@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    if request.method == "POST":
        oldpass = request.form.get("old")
        newpass = request.form.get("new")
        query = extract(db.execute("SELECT * FROM users where id = ?", (session["user_id"],)).fetchall())
        confirmation = request.form.get("confirmation")
        if not oldpass or not newpass or not confirmation:
            status = "Some fields are blank"
        # Incase user is a deleted user
        elif len(query) < 1:
            status = "User does not exist"
        elif check_password_hash(query[0]["password"], oldpass) == False:
            status = "Incorrect Password"
        elif not pass_validate(newpass,confirmation)== "Valid":
            status = pass_validate(newpass,confirmation)
        else:
            hash=generate_password_hash(newpass)
            db.execute("UPDATE users SET password=? where id=?",(hash,session["user_id"]))
            db.commit()
            status = "Password changed succesfully!"
        return render_template("changepass.html", status=status)
    return render_template("changepass.html")

# Change Username
@app.route("/changeusername", methods=["GET", "POST"])
@login_required
def changeusername():
    if request.method == "POST":
        new = request.form.get("new")
        query = extract(db.execute("SELECT * FROM users WHERE username = ?", (new,)).fetchall())
        # check if username is valid 
        if not new:
            status = "Username cannot be blank"
        elif not len(query) == 0:
            status = "Username already exists"
        else:
            db.execute("UPDATE users SET username=? WHERE id=?", (new,session["user_id"]))
            db.commit()
            session["username"] = new
            status = "Username changed succesfully"
        return render_template("changeusername.html", status=status)
    return render_template("changeusername.html")

## Table options ##
# Create a table
@app.route("/create", methods=["POST"])
@login_required
def create():
    # Create a table
    name = request.form.get("TableName")
    if not name:
        name = "default"
    db.execute("INSERT INTO tables(TableName,OwnerID) VALUES(?,?)", (name,session["user_id"]))
    db.commit()
    return redirect("/")

# Delete a table
@app.route("/DeleteTable", methods=["GET","POST"])
@login_required
def DeleteTable():
    TableID = request.args.get("table")
    # check if the user owns the table
    check=checker(TableID,session["user_id"])
    if not len(check) == 1:
        return render_template("not found.html")
    if request.method == "POST":
        try:
            request.form["choice"]
        except:
            return redirect(request.referrer)
        if request.form["choice"] == "Yes":
            db.execute("DELETE FROM tables WHERE OwnerID=? AND TableID=?", (session["user_id"], TableID))
            db.execute("DELETE FROM data WHERE OwnerID=? AND TableID=?", (session["user_id"], TableID))
            db.commit()
            return redirect("/")
        elif request.form["choice"] == "No":
            return redirect("/")
        else:
            return redirect("/")
    return render_template("delete table.html", Table=check)

# Copy a table
@app.route("/CopyTable")
@login_required
def CopyTable():
    TableID = request.args.get("table")
    # Check if the user owns the table
    check = checker(TableID,session["user_id"])
    if len(check) == 0:
        return render_template("not found.html")
    # Create new table
    db.execute("INSERT INTO tables(OwnerID, TableName) VALUES(?,?)",(session["user_id"],check[0]["TableName"]))
    db.commit()
    # Get the latest table the user created
    NewTable = extract(db.execute("SELECT * FROM tables WHERE OwnerID=? ORDER BY TableID DESC", (session["user_id"],)).fetchall())
    # Get the data from old table
    datas = extract(db.execute("SELECT * FROM data WHERE TableID=? AND OwnerID=?",(TableID,session["user_id"])).fetchall())
    for i in range(len(datas)):
        db.execute("INSERT INTO data(TableID,OwnerID,Name,Entries) VALUES(?,?,?,?)",(NewTable[0]["TableID"],session["user_id"],datas[i]["Name"],datas[i]["Entries"]))
    db.commit()
    return redirect("/")


# View a table
@app.route("/view")
def view():
    TableID = request.args.get("table")
    check=[]
    # Check if the table is available
    try: 
        # If there is a logged in account
        check = checker(TableID,session["user_id"])
        # If there is a looged in acount but is not owned by the user
        if len(check) == 0:
            check = checker(TableID,None)
    except:
        # If there is no logged in account
        check = checker(TableID,None)
    # if there was no table found that matches
    if not len(check) == 1:
        return render_template("not found.html")
    # Render the data
    data=extract(db.execute("SELECT * FROM data WHERE TableID=?",(TableID, )).fetchall())
    return render_template("view.html", data = data, TableInfo = check)

# Edit a table
@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    # Prepare the table
    TableID = request.args.get("table")
    # Check if the table is accessible by user
    check=checker(TableID,session["user_id"])
    if not len(check) == 1:
        return render_template("not found.html")
    # Obtain the data
    data=extract(db.execute("SELECT * FROM data WHERE TableID=? AND OwnerID = ?",(TableID, session["user_id"])).fetchall())
    # For Post requests (editting the table)
    if request.method == "POST":
        # Update the table based on the post request
        # Check if form["action"] exists if not redirect to previous page
        try:
            request.form["action"]
        except:
            return redirect(request.referrer)
        # Add a person to the table
        if request.form["action"] == "AddPerson":
                name=request.form.get("AddName")
                # Add a default name incase user does not input any Names
                if not name:
                    name = "Default"
                # Precaution incase the user inputs something that is not a number or negative values
                try:
                    entries=int(request.form.get("AddEntries"))
                    if entries < 0:
                        entries = 0
                except:
                    entries = 0
                # Insert the person to the database
                db.execute("INSERT INTO data(TableID, OwnerID, Name, Entries) VALUES(?,?,?,?)",(TableID, session["user_id"], name, entries))
                db.commit()
                # redirect to make the changes visible
                return redirect(request.referrer)
        # Delete Selected People
        elif request.form["action"] == "DeleteSelected":
            delete=request.form.getlist("DeleteID")
            for i in range(len(delete)):
                try:
                    # Delete Selected names while checking if user owns them
                    db.execute("DELETE FROM data WHERE NameID=? AND OwnerID=?",(delete[i],session["user_id"]))
                    db.commit()
                except:
                    return redirect(request.referrer)
            return redirect(request.referrer)
        # Update the table based on the editted values
        elif request.form["action"] == "UpdateTable":
            ids=request.form.getlist("ID")
            names=request.form.getlist("Name")
            entries=request.form.getlist("Entries")
            # Check if the values to be updated are valid
            if not len(ids) == len(names) and len(names) == len(entries):
                return redirect(request.referrer)
            # Update values in the table
            for i in range(len(ids)):
                # Precaution incase the user leaves a space blank or gives a negative integer
                if not names[i]:
                        names[i] = "default"
                try:    
                    if int(entries[i]) < 0:
                        entries[i] = 0
                except: 
                    entries[i] = 0
                try:
                    db.execute("UPDATE data SET Name=?, Entries=? WHERE NameID=? AND OwnerID=?",(names[i],entries[i],ids[i],session["user_id"]))
                    db.commit()
                except:
                    return redirect(request.referrer)
            return redirect(request.referrer)
        # Rename the table
        elif request.form["action"] == "RenameTable":
            TableName=request.form.get("TableName")
            if not TableName:
                return redirect(request.referrer)
            db.execute("UPDATE tables SET TableName=? WHERE TableID=? AND OwnerID=?",(TableName,TableID,session["user_id"]))
            db.commit()
            return redirect(request.referrer)
        # Change publicity of the table
        elif request.form["action"] == "ChangePublicity": 
            # Check if the table is Public or not then change accordingly
            if int(check[0]["IsPublic"]) == 0:
                db.execute("UPDATE tables SET IsPublic = 1 WHERE TableID=? AND OwnerID=?",(TableID,session["user_id"]))
                db.commit()
            elif int(check[0]["IsPublic"]) == 1:
                db.execute("UPDATE tables SET IsPublic = 0 WHERE TableID=? AND OwnerID=?",(TableID,session["user_id"]))
                db.commit()
            # Refresh to make changes visible
            return redirect(request.referrer)
        # If the post request is invalid return to previous page
        else:
            return redirect(request.referrer)
    # Render the table
    return render_template("edit.html", data = data,TableInfo = check)

## Misc ##
# Custom Not Found message
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('not found.html')

# About 
@app.route("/about")
def about():
    return render_template("about.html")

