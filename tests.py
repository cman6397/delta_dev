from flask import render_template,url_for,redirect,flash, json, jsonify
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
	
	household_query=db.session.query(Household.name.label('household_name'),func.sum(Account.balance).label('balance'),func.min(Account.opening_date).label('opening_date'), \
	func.count(Account.id).label('num_accounts'), Billing_Group.name.label('billing_group')).outerjoin(Account, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Household.id == Billing_Group.household_id).group_by(Household.id)
	households=household_query.all()

	billing_group_query=db.session.query(Billing_Group.name.label('Name'),func.sum(Account.balance).label('Balance'), \
	func.count(Account.id).label('Total Accounts'), Household.name.label('Household')).outerjoin(Account, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Household, Household.id == Billing_Group.household_id).group_by(Billing_Group.id)
	billing_groups=billing_group_query.all()

	accounts_query=db.session.query(Account.name.label('account_name'),Account.account_number.label('account_number'), Account.custodian.label('custodian'), \
	Account.opening_date.label('opening_date'), Account.balance.label('balance'), Household.name.label('household'),Billing_Group.name.label('billing_group'), \
	Fee_Structure.name.label('fee_structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	fee_structure_query=db.session.query(Fee_Structure.name.label('fee_structure'),Fee_Structure.frequency.label('frequency'),Fee_Structure.collection.label('collection'), \
	Fee_Structure.structure.label('structure'),Fee_Structure.valuation_method.label('valuation_method'),func.count(Account.id).label('num_accounts')). \
	outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	return success,msg

def json_testing():
	accounts_query=db.session.query(Account.name.label('account_name'),Account.account_number.label('account_number'), Account.custodian.label('custodian'), \
	Household.name.label('household'),Billing_Group.name.label('billing_group'), \
	Fee_Structure.name.label('fee_structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	accounts=accounts_query.all()
	keys=accounts[0].keys()
	json_struct=[]

	json_struct=[dict(zip([key for key in keys],row)) for row in accounts]

def show_table():
	fee_structure_query=db.session.query(Fee_Structure.name.label('fee_structure'),Fee_Structure.frequency.label('frequency'),Fee_Structure.collection.label('collection'), \
	Fee_Structure.structure.label('structure'),Fee_Structure.valuation_method.label('valuation_method'),func.count(Account.id).label('num_accounts')). \
	outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	fee_structures=fee_structures.all()
	for fee_struct in fee_structures:
		print(fee_struct)

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

		json_testing()

	#show_table()





