import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from dotenv import load_dotenv
import re
from flask_bcrypt import Bcrypt
from decimal import Decimal


# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")
bcrypt = Bcrypt(app)

# ------------------------ BEGIN FUNCTIONS ------------------------ #
# Function to retrieve DB connection
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    return conn

# Get all buckets from the "buckets" table of the db
# def get_all_buckets():
#     # Create a new database connection for each request
#     conn = get_db_connection()  # Create a new database connection
#     cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
#     # Query the db
#     query = "SELECT u.Username, b.BucketName, b.BucketDescription, b.BucketAllotted, b.BucketRemaining FROM User u JOIN Buckets b ON u.UserID = b.UserID WHERE u.Username = %s;"
#     vals = (session['username'],)
#     cursor.execute(query, vals)
#     # Get result and close
#     result = cursor.fetchall() # Gets result from query
#     conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
#     return result

def get_all_buckets():
    # Create a new database connection for each request
    userID = session['id']
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    query = "SELECT * from Buckets WHERE UserID = %s;"
    vals = (userID,)
    cursor.execute(query, vals)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# Get all transactions from the "transactions" table of the db
def get_all_transactions():
    # Create a new database connection for each request
    conn = get_db_connection()  # Create a new database connection
    cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
    # Query the db
    # TODO: Change this to tre query rather than the copy paste
    query = "SELECT u.Username, b.BucketName, b.BucketDescription, b.BucketAllotted, b.BucketRemaining FROM User u JOIN Buckets b ON u.UserID = b.UserID WHERE u.Username = %s;" 
    vals = (session['username'],)
    cursor.execute(query, vals)
    # Get result and close
    result = cursor.fetchall() # Gets result from query
    conn.close() # Close the db connection (NOTE: You should do this after each query, otherwise your database may become locked)
    return result

# ------------------------ END FUNCTIONS ------------------------ #


# ------------------------ BEGIN ROUTES ------------------------ #
# EXAMPLE OF GET REQUEST
@app.route("/", methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method == 'POST' and 'addTrans' in request.form:
        if 'date' in request.form and 'description' in request.form and 'amount' in request.form and 'date' in request.form and 'bucket' in request.form:
            date = request.form['date']
            description = request.form['description']
            amount = request.form['amount']
            bucket = request.form['bucket']
            conn = get_db_connection()  # Create a new database connection
            cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
            query = "SELECT * FROM Buckets WHERE BucketName = %s and UserID = %s;"
            vals = (bucket, session['id'],)
            cursor.execute(query, vals)
            bucketSQL = cursor.fetchone()
            conn.close() # Close the db connection
            bucketID = bucketSQL[0]
            conn = get_db_connection()  # Create a new database connection
            cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
            # Query the db
            query = "INSERT INTO Transactions (UserID, IsExpense, Amount, TransDate, Description, BucketID) VALUES (%s, %s, %s, %s, %s, %s);"
            if request.form.get('expense'):
                vals = (session['id'], 1, amount, date, description, bucketID,)
                bucketRemaining = Decimal(bucketSQL[4]) - Decimal(amount)
            else:
                vals = (session['id'], 0, amount, date, description, bucketID,)
                bucketRemaining = Decimal(bucketSQL[4]) + Decimal(amount)
            cursor.execute(query, vals)
            conn.commit() #Inserts username and password as new user into User table
            query = "UPDATE Buckets SET BucketRemaining = %s WHERE BucketID = %s;"
            vals = (bucketRemaining, bucketID,)
            cursor.execute(query, vals)
            conn.commit()
            conn.close() # Close the db connection
        else:
            msg = 'Please fill out all fields in the form !' # Call defined function to create transaction
        items = get_all_buckets() # Call defined function to get all items
        return render_template("index.html", items=items) # Return the page to be rendered
    if request.method == 'POST' and 'addBucket' in request.form:
        #TODO: Make this to create a bucket, rather than transactions
        if 'name' in request.form and 'description' in request.form and 'allocated' in request.form:
            name = request.form['name']
            description = request.form['description']
            allocated = request.form['allocated']
            conn = get_db_connection()  # Create a new database connection
            cursor = conn.cursor() # Creates a cursor for the connection, you need this to do queries
            query = "INSERT INTO Buckets (UserID, BucketName, BucketDescription, BucketAllotted, BucketRemaining) VALUES (%s, %s, %s, %s, %s);"
            vals = (session['id'], name, description, allocated, allocated,)
            cursor.execute(query, vals)
            conn.commit() #Inserts username and password as new user into User table
            conn.close() # Close the db connection
        else:
            msg = 'Please fill out all fields in the form !' # Call defined function to create transaction
        items = get_all_buckets() # Call defined function to get all items
        return render_template("index.html", items=items) # Return the page to be rendered
    if request.method == 'GET':
        items = get_all_buckets() # Call defined function to get all items
        return render_template("index.html", items=items) # Return the page to be rendered

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM User WHERE Username = %s;" #looks for user associated with account specified
        vals = (username,)
        cursor.execute(query, vals)
        account = cursor.fetchone()
        conn.close() # Close the db connection
        userID = account[0]
        username = account[1]
        password_hash = account[2]
        is_valid = bcrypt.check_password_hash(password_hash, password) #ensures password hash is the same as the one provided
        if account and is_valid: 
            session['logged_in'] = True #sets session variables
            session['id'] = userID
            session['username'] = username
            msg = 'Logged in successfully!'
            return render_template('index.html', msg = msg) #redirects to index.html
        else:
            msg = 'Incorrect username / password !' #redirects back to login saying either username or password was incorrect
    return render_template('login.html', msg = msg)
 
@app.route('/logout')
def logout():
    session.clear() #clears session variables
    return redirect(url_for('login')) #redirects to login
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form : #Ensures all fields in form used
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM User WHERE Username = %s;" #Looks for potential users that already have username
        vals = (username,)
        cursor.execute(query, vals)
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') #creates a bcrypt hash of password provided
            query = "INSERT INTO itc350.User (Username, PasswordHash, IsAdmin) VALUES (%s, %s, %s);"
            vals = (username, hashed_password, False,)
            cursor.execute(query, vals)
            conn.commit() #Inserts username and password as new user into User table
            conn.close() # Close the db connection
            msg = 'Registered successfully!'
            return render_template('login.html', msg = msg) #redirects to login page saying successful register
    elif request.method == 'POST': #redirects to register if username or password not provided
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/new-trans', methods =['POST'])
def newTrans():
    if not session.get('logged_in'):
        return render_template('login.html')
# ------------------------ END ROUTES ------------------------ #


# listen on port 8080
if __name__ == "__main__":
    app.run(port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
