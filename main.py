from flask import Flask, render_template
from flask_sqlalchemy import SQLALchemy
from flask_login import UserMixin
app = Flask(__name__)

db = SQLALchemy(main)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

class User(db.Model, UserMixin):
    id = db.Column(db.integer, primary_key=True)
    username = db.Column(db.string(30), nullable=False)
    password = db.Column(db.string(90), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True)