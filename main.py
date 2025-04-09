from flask import Flask, render_template, request, redirect, url_for, flash
from tinydb import TinyDB, Query
app = Flask(__name__)

db = TinyDB('uporabniki.json')
Uporabnik = Query()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    
    return render_template('login.html')

@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.get(Uporabnik.username == username)
        if user:
            return "Username already exists"
        
        db.insert({'username': username, 'password': password})
        return "Successfully registered"
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)