from flask import render_template,url_for,redirect,flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app.forms import LoginForm
from app.models import User, Account, Household
from app.content import account_view,household_view

@app.route('/')
def main():
    return redirect (url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if form.validate_on_submit():
        verified, message, user = form.verify_user()
        if verified:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/household/')
@login_required
def household():
    table=Household.query.all()
    return render_template('households.html',table=table, cols = household_view)

@app.route('/account/')
@login_required
def account():
    table=Account.query.all()
    return render_template('accounts.html',table=table, cols = account_view)

