from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = 'root'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
mysql = MySQLConnector(app,'login_registration')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def create():
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'password': md5.new(request.form['password']).hexdigest()
    }

    check = "SELECT email FROM users"
    
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    for i in (mysql.query_db(check)):
        if i['email'] == email:
            flash("Email already in database")
            return redirect('/')
    if len(email) < 1:
        flash("Email cannot be empty!")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!")
        return redirect('/')
    elif len(first_name) < 1:
        flash("First name cannot be empty!")
        return redirect('/')
    elif any(i.isdigit() for i in first_name) == True:
        flash("Invalid first name!")
        return redirect('/')
    elif len(last_name) < 1:
        flash("Last name cannot be empty!")
        return redirect('/')
    elif any(i.isdigit() for i in last_name) == True:
        flash("Invalid last name!")
        return redirect('/')
    elif len(password) < 8:
        flash("Password must contain at least eight characters!")
        return redirect('/')
    elif confirm_password != password:
        flash("Passwords must match!")
        return redirect('/')
    else:
        flash("Successfully Registered!")
        mysql.query_db(query, data)
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT * FROM users WHERE email = :email"
    data = {
        'email': request.form['email']
    }
    users = mysql.query_db(query, data)

    if len(users) > 0:
        user = users[0]
        if user['password'] == md5.new(request.form['password']).hexdigest():
            session['logged_id'] = user['id']
            return redirect("/dashboard")
        else:
            flash("Password doesn't match")
            return redirect('/')
    else: 
        flash ('No username found')
        return redirect('/')

@app.route("/dashboard")
def dashboard():
    flash("Logged In!")
    return "Logged In"

app.run(debug=True)