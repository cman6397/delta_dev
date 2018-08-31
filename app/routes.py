from flask import render_template,url_for,redirect,flash
from app import app
from app.forms import LoginForm

@app.route('/')
def index():
    return redirect (url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
    	flash('Login Successful')
    return render_template('login.html', title='Sign In', form=form)