from flask import render_template,url_for,redirect,flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func, label
from app import app
from app import db
from app.forms import LoginForm, HouseholdForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure
from app.content import account_view, household_view, fee_view

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
	household_query=db.session.query(func.sum(Account.balance).label('balance'),Household.name.label('household_name'),func.min(Account.opening_date).label('opening_date'), \
	func.count(Account.id).label('num_accounts'), Billing_Group.name.label('billing_group')).outerjoin(Household, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id).group_by(Household)

	households=household_query.all()
	return render_template('table_display.html',table=households, cols = household_view)

@app.route('/account/')
@login_required
def account():
	accounts_query=db.session.query(Account.name.label('account_name'),Account.account_number.label('account_number'), Account.custodian.label('custodian'), \
	Account.opening_date.label('opening_date'), Account.balance.label('balance'), Household.name.label('household'),Billing_Group.name.label('billing_group'), \
	Fee_Structure.name.label('fee_structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	accounts=accounts_query.all()
	return render_template('table_display.html',table=accounts, cols = account_view)

@app.route('/fee_structure/',methods=['GET', 'POST'])
@login_required
def fee_structure():

	fee_structure_query=db.session.query(Fee_Structure.name.label('fee_name'),Fee_Structure.frequency.label('frequency'),Fee_Structure.collection.label('collection'), \
	Fee_Structure.structure.label('structure'),Fee_Structure.valuation_method.label('valuation_method'),func.count(Account.id).label('num_accounts'), Fee_Structure.id.label('id')). \
	outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	if request.method == "POST":
		delete_keys= request.json
		print(delete_keys)

	fee_structures=fee_structure_query.all()
	return render_template('table_edit.html',table=fee_structures, cols = fee_view)

@app.route('/fee_structure/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fee_structures(id):
	return render_template('edit_fees.html')

@app.route('/dev/')
def dev():
	return render_template('dev.html')

