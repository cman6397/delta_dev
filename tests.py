from flask import render_template,url_for,redirect,flash
from flask_login import current_user, login_user
from app import app
from app import db
from app.forms import LoginForm
from app.models import User, Account, Household, Fee_Structure, Billing_Group
from passlib.hash import sha256_crypt
from app.content import account_view
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, label
import warnings
from sqlalchemy import exc as sa_exc

def create_user(username,password):
	registered=False
	message = "Username Taken"
	user = User.query.filter_by(username=username).first()
	if not user:
		user = User(username=username,password=password)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		message="User Registered"
		registered=True
	return registered,message

def remove_user(username):
	User.query.filter_by(username=username).delete()
	db.session.commit()

	print("User Removed")

def show_table():
	table = Account.query.all()
	for key in account_view:
		print(account_view[key])

def login_user(username,password):
	logged_in = False
	message="Invalid username or password."
	user = User.query.filter_by(username=username).first()
	if user and user.check_password(password):
		logged_in = True
		message="Login Successful"

	return logged_in, message

def household_account_relationships():
	success=True
	msg="Relationships Success"
	sample_account=Account.query.first()

	sample_household= Household.query.first()
	accounts= sample_household.accounts
	total_balance=0

	for account in accounts:
		total_balance+=account.balance

	total_balance=round(total_balance,2)
	household_balance=db.session.query(label('account_balance',func.sum(Account.balance))).filter(Account.household == sample_household).first()
	household_balance=round(household_balance[0],2)

	if household_balance != total_balance:
		success=False
	
	household_query=db.session.query(func.sum(Account.balance).label('balance'),Household.name.label('household_name'),func.min(Account.opening_date).label('opening_date'),func.count(Account.id).label('num_accounts'), Billing_Group.name.label('billing_group')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id).group_by(Household)
	households=household_query.all()
	
	for household in households:
		print(household.household_name,household.balance,household.opening_date, household.num_accounts,household.billing_group)


	return success,msg



if __name__ == '__main__':
	with warnings.catch_warnings():
		warnings.simplefilter("ignore", category=sa_exc.SAWarning)
		username='admin'
		password='1234'

		remove_user(username)

		status,msg = create_user(username,password)
		assert status
		print(msg)

		status,msg = login_user(username,password)
		assert status
		print(msg)

		status,msg = household_account_relationships()
		assert status
		print(msg)

	#show_table()




