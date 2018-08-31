from flask import render_template
from app import app
from app.forms import LoginForm

@app.route('/')
@app.route('/index/')
def index():
    return "Hello, World!"

@app.route('/login/')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)