from flask import render_template,url_for,redirect,flash, request,jsonify,json
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func, label
from sqlalchemy import exc, update
from app import app
from app import db
from app.forms import LoginForm, Fee_StructureForm, Billing_GroupForm, SplitForm
from app.models import User, Account, Household, Billing_Group, Fee_Structure, Split, Account_Split
from app.content import account_view, household_view, fee_view, dev_view
from sqlalchemy.orm import aliased
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
def num_serializer(query_result):
	serialized_data=[]
	for row in query_result:
		current_row=[]
		for x in range(0,len(row)):
			obj=row[x]
			if isinstance(obj,decimal.Decimal):
				if obj > 1:
					obj='${:,.2f}'.format(obj)
				elif obj>0.0001:
					obj=obj*100
					obj='{0:.2f}%'.format(obj)
			current_row.append(obj)
		serialized_data.append(current_row)
	return serialized_data


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
	from numpy import random

	total_AUM = db.session.query(func.sum(Account.balance).label('Balance')).first()[0]

	household_query=db.session.query(Household.name.label('Household'),func.sum(Account.balance).label('Balance'),(func.sum(Account.balance)/total_AUM).label('Percent of Book')). \
	outerjoin(Account, Account.household_id == Household.id).group_by(Household.id).order_by(func.sum(Account.balance).desc())

	account_query=db.session.query(Account.name.label('Account'),Account.balance.label('Balance'),(Account.balance/total_AUM).label('Percent of Book')). \
	order_by(Account.balance.desc())

	top_households=household_query.all()[0:5]
	top_accounts=account_query.all()[0:5]

	household_columns=top_households[0].keys()
	account_columns=top_accounts[0].keys()

	top_households=num_serializer(top_households)
	top_accounts=num_serializer(top_accounts)

	x_vals=[0]
	y_vals=[1000000]

	json_data=[]

	num_days=300
	rows=[[0,1000000]]
	for x in range(1,num_days):
		x_val = x
		y_val = y_vals[x-1]*(1+random.normal(0.002,0.015))

		x_vals.append(x_val)
		y_vals.append(y_val)

		json_data.append({'x': x_val,'y': y_val})
		rows.append([x_val,round(y_val,2)])

	return render_template('dashboard.html',Hchart_data=rows,x_vals=x_vals,y_vals=y_vals,json_data=json_data, top_households=top_households, household_columns=household_columns, top_accounts=top_accounts, account_columns=account_columns)

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
	Account_Fee_Location = aliased(Account)

	accounts_query = db.session.query(Account.id.label('id'),Account.name.label('Account Name'),Account.account_number.label('Account #'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Account.custodian.label('Custodian'),Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure'), Account.payment_source.label('Payment Source'), Account_Fee_Location.name.label('Fee Relocation'), func.group_concat(Split.name, "; ").label('Splits')) \
	.outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id).outerjoin(Account_Split).outerjoin(Split).group_by(Account.id) \
	.outerjoin(Account_Fee_Location, Account.fee_location) 

	accounts=accounts_query.all()
	keys=accounts[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in accounts]
	data=json.dumps({'data': data}, default = alchemyencoder)

	return data

@app.route('/account/',methods=['GET', 'POST'])
@login_required
def account():
	Account_Fee_Location = aliased(Account)

	accounts_query = db.session.query(Account.id.label('id'),Account.name.label('Account Name'),Account.account_number.label('Account #'), \
	Account.opening_date.label('Opening Date'), Account.balance.label('Balance'), Account.custodian.label('Custodian'),Household.name.label('Household'),Billing_Group.name.label('Billing Group'), \
	Fee_Structure.name.label('Fee Structure'), Account.payment_source.label('Payment Source'), Account_Fee_Location.name.label('Fee Relocation'), func.group_concat(Split.name, "; ").label('Splits')) \
	.outerjoin(Household, Account.household_id == Household.id).outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id) \
	.outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id).outerjoin(Account_Split).outerjoin(Split).group_by(Account.id) \
	.outerjoin(Account_Fee_Location, Account.fee_location) 
	
	
	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('text'))
	billing_group_query = db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('text'))

	fee_structures=fee_structure_query.all()
	billing_groups=billing_group_query.all()
	accounts=accounts_query.all()

	account_keys=accounts[0].keys()
	fee_structure_keys=fee_structures[0].keys()
	billing_group_keys=billing_groups[0].keys()

	fee_structures_json=[dict(zip([key for key in fee_structure_keys],row)) for row in fee_structures]
	billing_groups_json=[dict(zip([key for key in billing_group_keys],row)) for row in billing_groups]

	columns=[]

	for account_key in account_keys:
		columns.append({'data': account_key,'name': account_key})

	if request.method == "POST" and request.json:
		data=request.json
		assigned_accounts=data['accounts']
		if 'fee_structure' in data.keys():
			assigned_fee_structure=data['fee_structure'][0]
			db.session.query(Account).filter(Account.id.in_(assigned_accounts)).update({Account.fee_id : assigned_fee_structure},synchronize_session=False)
			try:
				db.session.commit()
			except exc.IntegrityError:
				db.session.rollback()
		elif 'billing_group' in data.keys():
			assigned_billing_group=data['billing_group'][0]
			db.session.query(Account).filter(Account.id.in_(assigned_accounts)).update({Account.billing_group_id : assigned_billing_group},synchronize_session=False)
			try:
				db.session.commit()
			except exc.IntegrityError:
				db.session.rollback()

	return render_template('account_display.html',fee_structures=fee_structures_json, billing_groups=billing_groups_json, data_link=url_for('account_data'), page_link = url_for('account'), columns=columns, title='Accounts')

@app.route('/account/<int:id>', methods=['GET', 'POST'])
@login_required
def account_details(id):
	Account_Fee_Location = aliased(Account)

	account_query = db.session.query(Account.id.label('id'),Account.name.label('account_name'),Account.account_number.label('account_number'), \
	Account.opening_date.label('opening_date'), Account.balance.label('balance'), Account.custodian.label('custodian'),Household.name.label('household'), \
	Billing_Group.id.label('billing_group_id'), Fee_Structure.id.label('fee_structure_id'), Account.payment_source.label('payment_source'), \
	Account_Fee_Location.id.label('fee_location_id'), func.group_concat(Split.id, ",").label('split_ids')).outerjoin(Household, Account.household_id == Household.id) \
	.outerjoin(Billing_Group, Account.billing_group_id == Billing_Group.id).outerjoin(Fee_Structure, Account.fee_id == Fee_Structure.id) \
	.outerjoin(Account_Split).outerjoin(Split).filter(Account.id == id).outerjoin(Account_Fee_Location, Account.fee_location).group_by(Account.id)

	accounts_query=db.session.query(Account.id.label('id'),Account.name.label('text'))
	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('text'))
	billing_group_query = db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('text'))
	split_query = db.session.query(Split.id.label('id'),Split.name.label('text'))

	fee_structures=fee_structure_query.all()
	billing_groups=billing_group_query.all()
	splits=split_query.all()
	accounts=accounts_query.all()
	account=account_query.first()

	fee_structure_keys=fee_structures[0].keys()
	billing_group_keys=billing_groups[0].keys()
	split_keys=splits[0].keys()
	accounts_keys=accounts[0].keys()
	account_keys=account.keys()

	accounts_json=[dict(zip([key for key in accounts_keys],row)) for row in accounts]
	fee_structures_json=[dict(zip([key for key in fee_structure_keys],row)) for row in fee_structures]
	billing_groups_json=[dict(zip([key for key in billing_group_keys],row)) for row in billing_groups]
	splits_json=[dict(zip([key for key in split_keys],row)) for row in splits]
	account_json=json.dumps([dict(zip([key for key in account_keys],account))],default=alchemyencoder)

	if request.method == "POST" and request.json:
		data=request.json

		edit_account=db.session.query(Account).filter(Account.id == id).first()
		fee_structure=db.session.query(Fee_Structure).filter(Fee_Structure.id == data["fee_structure"]).first()
		billing_group=db.session.query(Billing_Group).filter(Billing_Group.id == data["billing_group"]).first()
		fee_location=db.session.query(Account).filter(Account.id == data["fee_location"]).first()
		splits=db.session.query(Split).filter(Split.id.in_(data["splits"])).all()

		edit_account.fee_structure=fee_structure
		edit_account.fee_location=fee_location
		edit_account.billing_group=billing_group
		edit_account.splits=splits

		try:
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			return redirect(url_for('account_details'))
		#Not Redirecting!! Have to do it in javascript. Not Ideal!
		return redirect(url_for('account'))

	if account:
		return render_template('account_details.html',splits=splits_json,account_json=account_json,account=account, accounts=accounts_json, fee_structures=fee_structures_json, billing_groups=billing_groups_json,page_link=url_for('account'))
	
	return redirect(url_for('account'))


#********************** FEE STRUCTURE **************************
@app.route('/fee_structure_data/')
@login_required
def fee_structure_data():

	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('Fee Structure Name'),Fee_Structure.frequency.label('Frequency'), \
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
	fee_structure_query = db.session.query(Fee_Structure.id.label('id'),Fee_Structure.name.label('Fee Structure Name'),Fee_Structure.frequency.label('Frequency'), \
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

	billing_group_query=db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('Billing Group Name'), Household.name.label('Household'), \
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
	billing_group_query=db.session.query(Billing_Group.id.label('id'),Billing_Group.name.label('Billing Group Name'), Household.name.label('Household'), \
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

@app.route('/billing_group/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_billing_group(id):
	message = "Billing Group Name Taken"
	billing_group_query=db.session.query(Billing_Group).filter(Billing_Group.id == id)
	billing_group=billing_group_query.first()
	form = Billing_GroupForm(obj=billing_group)

	if billing_group:
		form = Billing_GroupForm(obj=billing_group)

		if form.validate_on_submit():
			form.populate_obj(billing_group)
			try:
				db.session.commit()
			except exc.IntegrityError:
				db.session.rollback()
				flash(message)
				return redirect(url_for('create_fee'))

			return redirect(url_for('billing_group'))
		return render_template('edit_template.html',form=form,page_link=url_for('billing_group'))
	return redirect(url_for('billing_group'))

@app.route('/billing_details/')
@login_required
def billing_details():
	total_AUM = db.session.query(func.sum(Account.balance).label('Balance')).first()[0]

	household_query=db.session.query(Household.name.label('Household'),func.sum(Account.balance).label('Balance'),(func.sum(Account.balance)/total_AUM).label('Percent of Book')). \
	outerjoin(Account, Account.household_id == Household.id).group_by(Household.id).order_by(func.sum(Account.balance).desc())

	account_query=db.session.query(Account.name.label('Account'),Account.balance.label('Balance'),(Account.balance/total_AUM).label('Percent of Book')). \
	order_by(Account.balance.desc())

	top_households=household_query.all()[0:5]
	top_accounts=account_query.all()[0:5]

	household_columns=top_households[0].keys()
	account_columns=top_accounts[0].keys()

	top_households=num_serializer(top_households)
	top_accounts=num_serializer(top_accounts)


	return render_template('billing_details.html',account_rows=top_households, account_columns=household_columns)

#********************** Billing Split **************************
@app.route('/split_data/')
@login_required
def split_data():

	split_query=db.session.query(Split.id.label('id'),Split.name.label('Split Name'),Split.splitter.label('Splitter'),Split.split_percentage.label('Split Percentage'))

	splits=split_query.all()
	keys=splits[0].keys()

	data=[dict(zip([key for key in keys],row)) for row in splits]
	data=json.dumps({'data': data}, default = alchemyencoder)
	
	return data

@app.route('/split/',methods=['GET', 'POST'])
@login_required
def split():

	split_query=db.session.query(Split.id.label('id'),Split.name.label('Split Name'),Split.splitter.label('Splitter'),Split.split_percentage.label('Split Percentage'))

	splits=split_query.first()
	keys=splits.keys()

	columns=[]
	for key in keys:
		columns.append({'data': key,'name': key})

	if request.method == "POST" and request.json:
		delete_keys = request.json
		print(delete_keys)
		delete_query = db.session.query(Split).filter(Split.id.in_(delete_keys))
		delete_query.delete(synchronize_session=False)
		db.session.commit()
		return redirect(url_for('split'))

	return render_template('table_edit.html', data_link=url_for('split_data'), page_link = url_for('split'), create_link = url_for('create_split'), columns=columns, title='Billing Splits')
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
	message = "Fee Structure Name Taken"
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


@app.route('/Split/create',methods=['GET', 'POST'])
@login_required
def create_split():
	message = "Billing Split Name Taken"
	form = SplitForm()
	if form.validate_on_submit():
		new_split = Split()
		form.populate_obj(new_split)
		try:
			db.session.add(new_split)
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			flash(message)
			return redirect(url_for('create_split'))

		return redirect(url_for('split'))

	return render_template('form_template.html', form=form, page_link=url_for('split'))

@app.route('/split/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_split(id):
	message = "Billing Split Name Taken"
	split_query=db.session.query(Split).filter(Split.id == id)
	split=split_query.first()
	form = SplitForm(obj=split)

	if split:

		if split.split_percentage:
			split.split_percentag=split.split_percentage*100

		form = SplitForm(obj=split)

		if form.validate_on_submit():
			form.populate_obj(split)
			try:
				db.session.commit()
			except exc.IntegrityError:
				db.session.rollback()
				flash(message)
				return redirect(url_for('create_fee'))

			return redirect(url_for('split'))
		return render_template('edit_template.html',form=form,page_link=url_for('split'))
	return redirect(url_for('split'))


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

	fee_structures_json=[dict(zip([key for key in fee_structure_keys],row)) for row in fee_structures]
	data_test=json.dumps(data_test, default = alchemyencoder)

	columns=[]

	for account_key in account_keys:
		columns.append({'data': account_key,'name': account_key})

	if request.method == "POST" and request.json:
		data=request.json
		if 'fee_structure' in data.keys():
			assigned_accounts=data['accounts']
			assigned_fee_structure=data['fee_structure'][0]
			db.session.query(Account).filter(Account.id.in_(assigned_accounts)).update({Account.fee_id : assigned_fee_structure},synchronize_session=False)
			try:
				db.session.commit()
				flash('Success')
			except exc.IntegrityError:
				db.session.rollback()


	#for account in accounts:
		#data_row=[]
		#for x in range (0,len(account_keys)):
			#data_row.append(account[x])
		#data_test.append(data_row)

	return render_template('dev.html',data_test=data_test,fee_structures=fee_structures_json, data_link=url_for('dev_data'), page_link = url_for('dev'), create_link = url_for('create_billing_group'), columns=columns, title='Accounts')





