from flask import render_template,url_for,redirect,flash, request,jsonify,json
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func, label
from sqlalchemy import exc
from app import app
from app import db
from app.forms import LoginForm, Fee_StructureForm, Billing_GroupForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure
from app.content import account_view, household_view, fee_view, dev_view
import datetime,decimal

def alchemyencoder(obj):
	if isinstance(obj, datetime.date):
		return obj.isoformat()
	elif isinstance(obj, decimal.Decimal):
		if obj > 1:
			return '${:,.2f}'.format(obj)
		elif obj>0.0001:
			return '{0:.2f}%'.format(obj*100)
		else:
			return ""


#********************** LOGIN/LOGOUT **************************

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

@app.route('/')
def main():
	return redirect (url_for('login'))

#********************** DASHBOARD **************************

@app.route('/dashboard/')
@login_required
def dashboard():
	return render_template('dashboard.html')

#********************** HOUSEHOLD **************************
@app.route('/household_data/')
@login_required
def household_data():
	household_query=db.session.query(Household.name.label('Household Name'),Billing_Group.name.label('Billing Group'),func.min(Account.opening_date).label('Opening Date'), \
	func.count(Account.id).label('Total Accounts'),func.sum(Account.balance).label('Balance')).outerjoin(Account, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Household.id == Billing_Group.household_id).group_by(Household.id)

	households=household_query.all()
	keys=households[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in households]
	data=json.dumps({'data': data}, default = alchemyencoder)

	return data

@app.route('/household/')
@login_required
def household():
	household_query=db.session.query(Household.name.label('Household Name'),Billing_Group.name.label('Billing Group'),func.min(Account.opening_date).label('Opening Date'), \
	func.count(Account.id).label('Total Accounts'),func.sum(Account.balance).label('Balance')).outerjoin(Account, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Household.id == Billing_Group.household_id).group_by(Household.id)
	
	household=household_query.first()
	keys=household.keys()

	columns=[]
	for key in keys:
		columns.append({'data': key,'name': key})

	return render_template('table_display.html', data_link=url_for('household_data'),columns=columns, title='Households')

#********************** ACCOUNT **************************
@app.route('/account_data/')
@login_required
def account_data():
	accounts_query = db.session.query(Account.name.label('Account Name'),Account.account_number.label('Account Number'), Account.custodian.label('Custodian'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	accounts=accounts_query.all()
	keys=accounts[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in accounts]
	data=json.dumps({'data': data}, default = alchemyencoder)

	return data

@app.route('/account/')
@login_required
def account():
	accounts_query = db.session.query(Account.name.label('Account Name'),Account.account_number.label('Account Number'), Account.custodian.label('Custodian'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)
	
	account=accounts_query.first()
	keys=account.keys()

	columns=[]
	for key in keys:
		columns.append({'data': key,'name': key})

	return render_template('table_display.html', data_link=url_for('account_data'),columns=columns, title='Accounts')

#********************** FEE STRUCTURE **************************
@app.route('/fee_structure_data/')
@login_required
def fee_structure_data():

	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('Fee Name'),Fee_Structure.frequency.label('Frequency'), \
	Fee_Structure.collection.label('Collection'),Fee_Structure.structure.label('Structure'),Fee_Structure.valuation_method.label('Valuation Method'), \
	func.count(Account.id).label('Total Accounts'),Fee_Structure.flat_rate.label('Flat Rate'),Fee_Structure.flat_fee.label('Flat Fee'), \
	Fee_Structure.quarterly_cycle.label('Quarterly Cycle')).outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)

	fee_structures=fee_structure_query.all()
	keys=fee_structures[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in fee_structures]
	data=json.dumps({'data': data}, default = alchemyencoder)
	
	return data

@app.route('/fee_structure/',methods=['GET', 'POST'])
@login_required
def fee_structure():
	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('Fee Name'),Fee_Structure.frequency.label('Frequency'), \
	Fee_Structure.collection.label('Collection'),Fee_Structure.structure.label('Structure'),Fee_Structure.valuation_method.label('Valuation Method'), \
	func.count(Account.id).label('Total Accounts'),Fee_Structure.flat_rate.label('Flat Rate'),Fee_Structure.flat_fee.label('Flat Fee'), \
	Fee_Structure.quarterly_cycle.label('Quarterly Cycle')).outerjoin(Account, Account.fee_id == Fee_Structure.id).group_by(Fee_Structure.name)
	fee_structures=fee_structure_query.first()
	keys=fee_structures.keys()

	columns=[]
	for key in keys:
		columns.append({'data': key,'name': key})

	if request.method == "POST" and request.json:
		delete_keys = request.json
		delete_query = db.session.query(Fee_Structure).filter(Fee_Structure.id.in_(delete_keys))
		delete_query.delete(synchronize_session=False)
		db.session.commit()
		return redirect(url_for('fee_structure'))

	return render_template('table_edit.html', data_link=url_for('fee_structure_data'), page_link = url_for('fee_structure'), create_link = url_for('create_fee'),columns=columns, title='Fee Structures')

#********************** BILLING GROUP **************************
@app.route('/billing_group_data/')
@login_required
def billing_group_data():

	billing_group_query=db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('Name'), Household.name.label('Household'), \
	func.count(Account.id).label('Total Accounts'),func.sum(Account.balance).label('Balance')).outerjoin(Account, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Household, Household.id == Billing_Group.household_id).group_by(Billing_Group.id)

	billing_groups=billing_group_query.all()
	keys=billing_groups[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in billing_groups]
	data=json.dumps({'data': data}, default = alchemyencoder)
	
	return data

@app.route('/billing_group/',methods=['GET', 'POST'])
@login_required
def billing_group():
	billing_group_query=db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('Name'), Household.name.label('Household'), \
	func.count(Account.id).label('Total Accounts'),func.sum(Account.balance).label('Balance')).outerjoin(Account, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Household, Household.id == Billing_Group.household_id).group_by(Billing_Group.id)

	billing_groups=billing_group_query.first()
	keys=billing_groups.keys()

	columns=[]
	for key in keys:
		columns.append({'data': key,'name': key})

	if request.method == "POST" and request.json:
		delete_keys = request.json
		delete_query = db.session.query(Billing_Group).filter(Billing_Group.id.in_(delete_keys))
		delete_query.delete(synchronize_session=False)
		db.session.commit()
		return redirect(url_for('billing_group'))

	return render_template('table_edit.html', data_link=url_for('billing_group_data'), page_link = url_for('billing_group'), create_link = url_for('create_billing_group'), columns=columns, title='Billing Groups')


#***************************** FORMS ******************************************

@app.route('/fee_structure/create',methods=['GET', 'POST'])
@login_required
def create_fee():
	message = "Fee Structure Name Taken"
	form = Fee_StructureForm()
	if form.validate_on_submit():
		new_fee_structure=Fee_Structure()
		form.populate_obj(new_fee_structure)
		try:
			db.session.add(new_fee_structure)
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			flash(message)
			return redirect(url_for('create_fee'))


		return redirect(url_for('fee_structure'))

	return render_template('form_template.html', form=form,page_link=url_for('fee_structure'))

@app.route('/fee_structure/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_fee_structure(id):
	fee_structure_query=db.session.query(Fee_Structure).filter(Fee_Structure.id == id)
	fee_structure=fee_structure_query.first()
	form = Fee_StructureForm(obj=fee_structure)

	if fee_structure:

		if fee_structure.flat_rate:
			fee_structure.flat_rate=fee_structure.flat_rate*100

		form = Fee_StructureForm(obj=fee_structure)

		if form.validate_on_submit():
			form.populate_obj(fee_structure)
			try:
				db.session.commit()
			except exc.IntegrityError:
				db.session.rollback()
				flash(message)
				return redirect(url_for('create_fee'))

			return redirect(url_for('fee_structure'))
		return render_template('edit_template.html',form=form,page_link=url_for('fee_structure'))
	return redirect(url_for('fee_structure'))

@app.route('/billing_group/create',methods=['GET', 'POST'])
@login_required
def create_billing_group():
	message = "Billing Group Name Taken"
	form = Billing_GroupForm()
	if form.validate_on_submit():
		new_billing_group = Billing_Group()
		form.populate_obj(new_billing_group)
		try:
			db.session.add(new_billing_group)
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			flash(message)
			return redirect(url_for('create_billing_group'))

		return redirect(url_for('billing_group'))

	return render_template('form_template.html', form=form, page_link=url_for('billing_group'))


@app.route('/fee_structure_assign/<int:id>', methods=['GET', 'POST'])
@login_required
def assign_fee_structure(id):
	fee_structure_query=db.session.query(Fee_Structure).filter(Fee_Structure.id == id)
	fee_structure=fee_structure_query.first()

	accounts_query=db.session.query(Account.name.label('Name'),Account.account_number.label('Account Number'), \
	Account.custodian.label('Custodian'), Account.balance.label('Balance')).outerjoin(Fee_Structure, Fee_Structure.id == Account.fee_id) \
	.outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group,Account.billing_group_id == Billing_Group.id). \
	filter(Fee_Structure.id == id)
	accounts=accounts_query.all()

	columns=accounts[0].keys()

	if fee_structure:
		return render_template('assign_template.html', fee_structure=fee_structure, accounts=accounts,columns=columns)

	return redirect(url_for('fee_structure'))

#********************** DEV **************************
@app.route('/dev_data/')
@login_required
def dev_data():

	accounts_query = db.session.query(Account.id.label('id'),Account.name.label('Account Name'),Account.account_number.label('Account Number'), Account.custodian.label('Custodian'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)

	accounts=accounts_query.all()
	keys=accounts[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in accounts]
	data=json.dumps({'data': data}, default = alchemyencoder)
	
	return data

@app.route('/dev/',methods=['GET', 'POST'])
@login_required
def dev():
	accounts_query = db.session.query(Account.id.label('id'),Account.name.label('Account Name'),Account.account_number.label('Account Number'), Account.custodian.label('Custodian'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure')).outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id)
	
	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('text'))

	fee_structures=fee_structure_query.all()
	accounts=accounts_query.all()

	account_keys=accounts[0].keys()
	fee_structure_keys=fee_structures[0].keys()

	data_test=[]
	for account in accounts:
		data_row=[]
		for x in range (0,len(account_keys)):
			data_row.append(account[x])
		data_test.append(data_row)
		
	fee_structures_json=[dict(zip([key for key in fee_structure_keys],row)) for row in fee_structures]
	data_test=json.dumps(data_test, default = alchemyencoder)

	columns=[]

	for account_key in account_keys:
		columns.append({'data': account_key,'name': account_key})

	return render_template('dev.html',data_test=data_test,fee_structures=fee_structures_json, data_link=url_for('dev_data'), page_link = url_for('billing_group'), create_link = url_for('create_billing_group'), columns=columns, title='Accounts')





