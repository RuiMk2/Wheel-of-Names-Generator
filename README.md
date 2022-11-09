# Wheel of Names Generator
#### Video Demo:  <URL HERE>
#### Description: This is a Wheel of names generator which aims to help my guildmates, and hopefully other users as well to keep track of entries, and make it easier to use them for the website Wheel of Names. This is also done as part of my Final Project for CS50. The app uses Flask, HTML, and JavaScript to fully function. This webapp has a user login system which allows different users to manage their own tables. Users have the ability to create, edit, copy, delete, rename, and make their tables available to be viewed by other people. A table consists of names of people, along with their number of entries, also a copy button is available to allow the user to have the names and entries be copied to their clipboard and be ready to be pasted to the wheel of names website. 
#### For this webapp I tried to make my own CS50 like version of db.execute to challenge myself to do website without the training wheels, but still a majority of this webapp is inspired by the problem set 9 (finance) of  CS50.
## Contents of the App:
### /static
#### -Used to keep the files that are used for static websites.These are usually the assets the that are used in the program
#### -copy.js is a javascript used to implement the copy to clipboard function of the app
#### -styles.css the cascading style sheets used to design the front end of the app
#### -The png files that were used here are for design purposes usually to show logos.
### /templates
#### -Keeps the html files that are rendered as needed while the app is running
#### -Uses jinja syntax to change the contents of the webpage while keeping the designated layout
#### -layout.html contains the main layout the webapp will follow
### app.py 
#### -Contains the back end of the app
#### -You may notice that I always query the OwnerID in most queries, I decided to do this to ensure that the user only gets to access the data they own even if they decided to mess with the html via inspect element.
#### - `def index()` the main menu of the app, shows the user what tables their own and the options they have
#### -`def register()` allows the user to create an account for the app, the user must input a valid username and password in order to register. Once a user has completed all prerequisites the password they entered will be hashed for security purposes and the credentials they entered will be added to the database
#### -`def login()` is used to log the user in the app, it will query to the database to check if the user is registered in the database and if the credentials they entered matches the one in the database, if the credentials matched the user is then logged in and they get their session saved.
#### `def logout()` clears the session of the user and redirects them to the login page this allows another user to login 
#### `def changepass()` allows the user to change their passwords. it uses the `def pass_validate(password,confirmation)` function to check if the user typed a valid password. Once all the requirements are met the user's information in the database will be updated
#### `def changeusername()` allows the user to change usernames, it first checks if it is a valid username or not. If the user entered a valid username it will the update the user's credentials in the database
#### `def create()` allows the user to create a table. If the user doesnt name the table it will be given the default Table name. It will insert the new table into the database
#### `def DeleteTable()` this gives a confirmation message if the user wants to delete the table, if yes it will delete the selected table from the database, if no it will redirect the user to the main menu
#### `def CopyTable()` allows the user to Copy a table, it takes the name and data of the previous table and copies it to a new one. For this function I decided to use GET method to allow this function to be used via the `<a href="">` tag.
#### `def view()` this allows users to view tables. It checks if the table is in public or not. If it is in public the table is shown to everyone even if they dont own the table, if the table is in private only the owner of the table can view it
#### `def edit()` this is used to edit the tables. I designed it to take multiple POST requests so the user has multiple options to edit the table. If the POST request is `AddPerson` it takes user input and Adds the input to the database, if the inputs are blank or invalid they are changed to default. If the POST request is `DeleteSelected` it will get the ids of the selected names and delete them to the database accordingly. If the POST request is `UpdateTable` it will take all the items in the table of the user and update them accordingly. If the POST request is `RenameTable` it will Update the table name to what the user has entered in the text box. If the POST request is `ChangePublicity` it will change the Publicity of the table, if it is in private it will change it to public, and vice versa.
#### `def page_not_found(e)` this is a function provided by flask which allows me to give the user a custom error message when they get a 404 code
#### `def about()` renders the about page which shows information about the website and its creator
### tools.py
#### - other functions that are not related to rendering html but still used to create the app
#### - `def extract(query)` is used to extract the query and return it as a list of dictionary 
#### -`def checker(TableID, UserID)` makes queries to the database to know if the user is allowed to view or edit the table. It returns the table if the user is allowed to view or edit it
#### -`def pass_validate(password,confirmation)` checks if the entered password matches the set conditions
#### -`def login_required(f)` flask's function that checks if the user has an account logged in, if not it redirects the user to the login page
### database.db
#### -The main database of the app where the user data and the table data is stored
### requirements.txt
#### -Contains information on what are required to make the app run
### Sources for some codes that helped make the app possible:
#### [Get the information in sqlite as a dict](https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query)
#### [Multiple submit options for post requests](https://stackoverflow.com/questions/43811779/use-many-submit-buttons-in-the-same-form)
#### [Jinja White space control](https://ttl255.com/jinja2-tutorial-part-3-whitespace-control/#:~:text=Jinja2%20allows%20us%20to%20manually,or%20after%20the%20block%2C%20respectively.)
#### [Copy text area to clipboard](https://stackoverflow.com/questions/37658524/copying-text-of-textarea-in-clipboard-when-button-is-clicked)
#### [New line Substitute for textarea](https://stackoverflow.com/questions/8627902/how-to-add-a-new-line-in-textarea-element)
