from flask import render_template,url_for,redirect,flash, request,jsonify,json
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func, label
from app import app
from app import db
from app.forms import LoginForm, HouseholdForm, Fee_StructureForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure
from app.content import account_view, household_view, fee_view, dev_view
import datetime,decimal

def alchemyencoder(obj):
	if isinstance(obj, datetime.date):
		return obj.isoformat()
	elif isinstance(obj, decimal.Decimal):
		return '${:,.2f}'.format(obj)

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
	return render_template('household_display.html',cols = household_view)

@app.route('/household_data/')
@login_required
def household_data():
	household_query=db.session.query(func.sum(Account.balance).label('balance'),Household.name.label('household_name'),func.min(Account.opening_date).label('opening_date'), \
	func.count(Account.id).label('num_accounts'), Billing_Group.name.label('billing_group')).outerjoin(Household, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id).group_by(Household)

	households=household_query.all()
	keys=households[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in households]
	return (json.dumps({'data': data}, default = alchemyencoder))

@app.route('/account/')
@login_required
def account():
	return render_template('account_display.html', cols = account_view)

@app.route('/account_data/')
@login_required
def account_data():
	accounts_query = db.session.query(Account.name.label('account_name'),Account.account_number.label('account_number'), Account.custodian.label('custodian'), \
	Account.opening_date.label('opening_date'), Account.balance.label('balance'), Household.name.label('household'),Billing_Group.name.label('billing_group'), \
	Fee_Structure.name.label('fee_structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	account_names=['Id','Account Name', 'Account Number', 'Custodian', 'Opening Date', 'Balance', 'Household', 'Billing Group']

	accounts=accounts_query.all()
	keys=accounts[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in accounts]
	return (json.dumps({'data': data}, default = alchemyencoder))


@app.route('/fee_structure_data/')
@login_required
def fee_structure_data():

	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('fee_name'),Fee_Structure.frequency.label('frequency'), \
	Fee_Structure.collection.label('collection'),Fee_Structure.structure.label('structure'),Fee_Structure.valuation_method.label('valuation_method'), \
	func.count(Account.id).label('num_accounts')).outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	fee_structures=fee_structure_query.all()
	keys=fee_structures[0].keys()

	fee_names=['Id', 'Name', 'Frequency', 'Collection', 'Structure', 'Valuation Method', 'No. Accounts']

	columns=[]
	count=0
	for key in keys:
		columns.append({'data': key,'name': fee_names[count]})
		count+=1

	data=[dict(zip([key for key in keys],row)) for row in fee_structures]
	data=json.dumps({'data': data , 'columns': columns}, default = alchemyencoder)
	
	return data

@app.route('/fee_structure/',methods=['GET', 'POST'])
@login_required
def fee_structure():
	if request.method == "POST" and request.json:
		delete_keys = request.json
		print(delete_keys)
		delete_query = db.session.query(Fee_Structure).filter(Fee_Structure.id.in_(delete_keys))
		delete_query.delete(synchronize_session=False)
		db.session.commit()
		return redirect(url_for('fee_structure'))

	return render_template('table_edit.html',cols=fee_view, data_link=url_for('fee_structure_data'), page_link = url_for('fee_structure'), create_link = url_for('create_fee'))

@app.route('/dev_data/')
@login_required
def dev_data():

	fee_structure_query = db.session.query(Fee_Structure.name.label('fee_name'),Fee_Structure.frequency.label('frequency'),Fee_Structure.collection.label('collection'), \
	Fee_Structure.structure.label('structure'),Fee_Structure.valuation_method.label('valuation_method'),func.count(Account.id).label('num_accounts'), Fee_Structure.id.label('id')). \
	outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	fee_structures=fee_structure_query.all()
	keys=fee_structures[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in fee_structures]
	data=json.dumps({'data': data}, default = alchemyencoder)
	
	return data

@app.route('/dev/',methods=['GET', 'POST'])
@login_required
def dev():
	if request.method == "POST" and request.json:
		delete_keys = request.json
		print(delete_keys)
		delete_query = db.session.query(Fee_Structure).filter(Fee_Structure.id.in_(delete_keys))
		delete_query.delete(synchronize_session=False)
		db.session.commit()
		return redirect(url_for('dev'))

	return render_template('dev.html',cols=fee_view)


@app.route('/fee_structure/create',methods=['GET', 'POST'])
@login_required
def create_fee():
	form = Fee_StructureForm()
	if form.validate_on_submit():
		name = form.name.data
		frequency = form.frequency.data
		collection = form.collection.data
		structure = form.structure.data
		valuation_method = form.valuation_method.data

		fee_structure=Fee_Structure(name=name,frequency=frequency,collection=collection,structure=structure,valuation_method=valuation_method)
		db.session.add(fee_structure)
		db.session.commit()
		return redirect(url_for('fee_structure'))

	return render_template('form_template.html', methods=['GET', 'POST'], form=form)

@app.route('/fee_structure/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fee_structures(id):
	return render_template('edit_fees.html')




