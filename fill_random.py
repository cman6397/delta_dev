from app import app
from app import db
from app.models import Account, Household, Fee_Structure, Billing_Group, Split, Account_Split, Account_History
import random
import time
from datetime import datetime, timedelta
from numpy import random as random_np

names=['Liam','Noah','William','James','Logan','Benjamin','Mason','Elijah','Oliver','Jacob','Lucas','Michael','Alexander','Ethan','Daniel','Matthew','Aiden','Henry',
'Joseph','Jackson','Samuel','Sebastian','David','Carter','Wyatt','Jayden','John','Owen','Dylan','Luke','Gabriel','Anthony','Isaac','Grayson','Jack','Julian','Levi',
'Christopher','Joshua','Andrew','Lincoln','Mateo','Ryan','Jaxon','Nathan','Aaron','Isaiah','Thomas','Charles','Caleb','Josiah','Christian','Hunter','Eli','Jonathan',
'Connor','Landon','Adrian','Asher','Cameron','Leo','Theodore','Jeremiah','Hudson','Robert','Easton','Nolan','Nicholas','Ezra','Colton','Angel','Brayden','Jordan',
'Dominic','Austin','Ian','Adam','Elias','Jaxson','Greyson','Jose','Ezekiel','Carson','Evan','Maverick','Bryson','Jace','Cooper','Xavier','Parker','Roman','Jason',
'Santiago','Chase','Sawyer','Gavin','Leonardo','Kayden','Ayden','Jameson']

custodians=['Td Ameritrade','Charles Schwab']
payment_sources=['Custodian Billed', 'Directly Billed']

households=['Chris Household','Nick Household','Andrew Household','Billy Household','Tom Household']
billing_groups = ['Chris Billing_Group','Nick Billing_Group','Andrew Billing_Group','Billy Billing_Group','Tom Billing_Group']

fee_names=['1.0 percent Annual','2.0 percent Annual','0.5 percent Annual','0.7 percent Annual', '1.5 percent Annual']
frequencies = ['Quarterly', 'Monthly']
collections = ['Advance with Proration', 'Arrears', 'Advance']
structures = ['Flat Rate', 'Flat Fee', 'Favor']
valuation_methods = ['Ending Period Balance', 'Average Daily Balance']
quarterly_cycles=['Mar-Jun-Sep-Dec','Feb-May-Aug-Nov','Jan-Apr-Jul-Oct']

split_names=['Jackie: 10%','Naylor: 20%','Vanclef:60%']
splitters=['Jackie','Naylor','Vanclef']
splits=[.1,.2,.6]

def generate_fee_structures():
	Fee_Structure.query.delete()
	for x in range(0,10):
		for fee_name in fee_names:
			name=fee_name + str(x)
			frequency=random.choice(frequencies)
			collection=random.choice(collections)
			structure=random.choice(structures)
			valuation_method=random.choice(valuation_methods)
			flat_rate=None
			flat_fee=None
			quarterly_cycle=''
			if structure == 'Flat Rate':
				flat_rate=round(random.uniform(0,0.1),4)
			elif structure == 'Flat Fee':
				flat_fee=round(random.uniform(500,10000),2)
			if frequency=='Quarterly':
				quarterly_cycle=random.choice(quarterly_cycles)

			fee_structure=Fee_Structure(name=name,frequency=frequency,collection=collection,structure=structure,valuation_method=valuation_method, flat_rate=flat_rate,flat_fee=flat_fee, quarterly_cycle=quarterly_cycle)
			db.session.add(fee_structure)

def generate_splits():
	Split.query.delete()
	count=0
	for split_name in split_names:
		name=split_name
		splitter=splitters[count]
		split=splits[count]

		new_split=Split(name=name,splitter=splitter,split_percentage=split)
		db.session.add(new_split)

		count+=1

def generate_households():
	Household.query.delete()
	for x in range(0,10):
		for household_name in households:
			name=household_name + str(x)
			household=Household(name=name)
			db.session.add(household)

def sample_household_billing_group_fees():
	households=Household.query.all()
	billing_groups=Billing_Group.query.all()
	fees=Fee_Structure.query.all()

	num_households=len(households)
	rand_int = random.randint(0,num_households-1)

	household=households[rand_int]
	billing_group=billing_groups[rand_int]
	fee=random.choice(fees)

	return household,billing_group,fee

def generate_billing_groups():
	Billing_Group.query.delete()

	households=Household.query.all()

	for y in range(0,10):
		for x in range (0,len(billing_groups)):
			name = billing_groups[x] + str(y)
			household=households[y*len(billing_groups)+x]
			billing_group = Billing_Group(name=name,household=household)
			db.session.add(billing_group)


def account_values():
	account = random.randint(1000000,100000000)
	balance = round(random.uniform(1000,500000),2)

	year = random.randint(2016, 2017)
	month = random.randint(1, 12)
	day = random.randint(1, 28)
	date = datetime(year, month, day)

	return account,balance,date

def generate_accounts():
	
	Account.query.delete()
	account_numbers=[]
	count=0
	for x in range(0,10):
		for name in names:
			account_number,balance,date=account_values()
			while account_number in account_numbers:
				account_number,balance,date=account_values()

			account_numbers.append(account_number)
			custodian=random.choice(custodians)
			payment_source=random.choice(payment_sources)

			household,billing_group,fee_structure=sample_household_billing_group_fees()

			account = Account(name=name,account_number=account_number,custodian=custodian,opening_date=date,balance=balance, payment_source=payment_source,household=household,billing_group=billing_group,fee_structure=fee_structure)
			db.session.add(account)

def generate_history():
	Account_History.query.delete()
	accounts = db.session.query(Account).all()
	for account in accounts:
		history_helper(account)

def history_helper(account,days=365):
	balance = float(account.balance)
	date = datetime(2019, 1, 1)

	for x in range (0,days):
		account_history=Account_History(account=account,balance=balance,date=date)
		date = date - timedelta(days=1)
		balance = balance*(1+random_np.normal(-0.001,0.050))
		db.session.add(account_history)

def add_fee_locations():
	accounts=db.session.query(Account).all()[1:5]
	first_account=db.session.query(Account).first()
	for account in accounts:
		account.fee_location=first_account

def check_fee_locations():
	accounts=db.session.query(Account).all()[0:5]
	for account in accounts:
		print(account.fee_location)

def add_splits():
	accounts=db.session.query(Account).all()[0:20]
	splits=db.session.query(Split).all()

	for account in accounts:
		account.splits.append(random.choice(splits))
	

if __name__ == '__main__':
	generate_fee_structures()
	generate_households()
	generate_billing_groups()
	generate_accounts()
	generate_splits()
	add_fee_locations()
	add_splits()
	generate_history()

	db.session.commit()

