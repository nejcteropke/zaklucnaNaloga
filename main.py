from flask import Flask, render_template, request, redirect, url_for, flash
from tinydb import TinyDB, Query
app = Flask(__name__)

db = TinyDB('uporabniki.json')
Uporabnik = Query()
app.secret_key = 'matijajepeder'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.get(Uporabnik.username == username)
        if user and user['password'] == password:
            #flash('Login Successful')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match")
            return render_template('register.html')
        
        user = db.get(Uporabnik.username == username)
        if user:
            flash("Username already exists")
            return render_template('register.html')
        
        db.insert({'username': username, 'password': password})
        #flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)