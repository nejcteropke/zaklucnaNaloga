from flask import Flask, render_template, request, redirect, url_for, flash, session
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
            session['username'] = username
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
        return redirect(url_for('setup_profile'))
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You need to login')
        return(url_for('login'))
    
    username = session['username']
    user = db.get(Uporabnik.username == username)

    if not user:
        #flash('User not found')
        return redirect(url_for('home'))
    return render_template('profile.html', user = user)

@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')

@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if request.method == 'POST':
        username = session['username']
        name = request.form.get('name')
        surname = request.form.get('surname')
        genre = request.form.get('genre')
        instrument = request.form.get('instrument')
        location = request.form.get('location')
        goals = request.form.get('goals')
        experience = request.form.get('experience')

        db.upsert({
            'name': name,
            'surname': surname,
            'genre': genre,
            'instrument': instrument,
            'location': location,
            'goals': goals,
            'experience': experience
        }, Uporabnik.username == username)
        return redirect(url_for('login'))
    return render_template('setup_profile.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    #flash('Logged out successfully')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)