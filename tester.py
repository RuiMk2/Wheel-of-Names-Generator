import sqlite3

from tools import extract
from werkzeug.security import check_password_hash, generate_password_hash

db=sqlite3.connect("database.db")
db.row_factory=sqlite3.Row

Tableid=1
query=extract(db.execute("SELECT * FROM users WHERE id=?",(5,)).fetchall())
print (query)

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

password="nananana"
test=has_numbers(password)
print(test)

password=("123456789aaaa")
hash=generate_password_hash(password)
hash2="nyaan"
check=check_password_hash(hash,password)
print(check)