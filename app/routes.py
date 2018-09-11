from flask import render_template,url_for,redirect,flash
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func, label
from app import app
from app import db
from app.forms import LoginForm, HouseholdForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure
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

@app.route('/household/',methods=['GET', 'POST'])
@login_required
def household():
	household_query = household_query=db.session.query(func.sum(Account.balance).label('balance'),Household.name.label('household_name'),func.min(Account.opening_date).label('opening_date'),func.count(Account.id).label('num_accounts'), Billing_Group.name.label('billing_group')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id).group_by(Household)
	table=household_query.all()
	return render_template('households.html',table=table, cols = household_view)

@app.route('/account/')
@login_required
def account():
	table=Account.query.all()
	return render_template('accounts.html',table=table, cols = account_view)

@app.route('/household/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_household(id):
	return render_template('edit_household.html')
