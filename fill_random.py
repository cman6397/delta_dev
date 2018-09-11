from app import app
from app import db
from app.models import Account, Household, Fee_Structure, Billing_Group
from app.content import account_view,household_view
import random
import time
from datetime import datetime

names=['Liam','Noah','William','James','Logan','Benjamin','Mason','Elijah','Oliver','Jacob','Lucas','Michael','Alexander','Ethan','Daniel','Matthew','Aiden','Henry',
'Joseph','Jackson','Samuel','Sebastian','David','Carter','Wyatt','Jayden','John','Owen','Dylan','Luke','Gabriel','Anthony','Isaac','Grayson','Jack','Julian','Levi',
'Christopher','Joshua','Andrew','Lincoln','Mateo','Ryan','Jaxon','Nathan','Aaron','Isaiah','Thomas','Charles','Caleb','Josiah','Christian','Hunter','Eli','Jonathan',
'Connor','Landon','Adrian','Asher','Cameron','Leo','Theodore','Jeremiah','Hudson','Robert','Easton','Nolan','Nicholas','Ezra','Colton','Angel','Brayden','Jordan',
'Dominic','Austin','Ian','Adam','Elias','Jaxson','Greyson','Jose','Ezekiel','Carson','Evan','Maverick','Bryson','Jace','Cooper','Xavier','Parker','Roman','Jason',
'Santiago','Chase','Sawyer','Gavin','Leonardo','Kayden','Ayden','Jameson']

custodians=['Td Ameritrade','Charles Schwab']

households=['Household1','Households2','Household3','Household4','Household5']
billing_groups = ['Billing_Group1','Billing_Group2','Billing_Group3','Billing_Group4','Billing_Group5']

fee_names=['1.0 percent Annual','2.0 percent Annual','0.5 percent Annual','0.7 percent Annual', '1.5 percent Annual']
frequencies = ['Quarterly', 'Monthly']
collections = ['Advance with Proration', 'Arrears', 'Advance']
structures = ['Flat Rate', 'Flat Fee', 'Favor']
valuation_methods = ['Ending Period Balance', 'Average Daily Balance']

def generate_fee_structures():
	Fee_Structure.query.delete()
	for fee_name in fee_names:

		name=fee_name
		frequency=random.choice(frequencies)
		collection=random.choice(collections)
		structure=random.choice(structures)
		valuation_method=random.choice(valuation_methods)

		fee_structure=Fee_Structure(name=name,frequency=frequency,collection=collection,structure=structure,valuation_method=valuation_method)
		db.session.add(fee_structure)

def generate_households():
	Household.query.delete()

	for household_name in households:
		household=Household(name=household_name)
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

	for x in range (0,len(billing_groups)):
		name = billing_groups[x]
		household=households[x]
		billing_group = Billing_Group(name=name,household=household)
		db.session.add(billing_group)


def random_values():
	account = random.randint(1000000,100000000)
	balance = round(random.uniform(1,10000000),2)

	year = random.randint(2016, 2018)
	month = random.randint(1, 12)
	day = random.randint(1, 28)
	date = datetime(year, month, day)

	return account,balance,date

def generate_accounts():
	
	Account.query.delete()
	account_numbers=[]

	for name in names:
		account_number,balance,date=random_values()
		while account_number in account_numbers:
			account_number,balance,date=random_values()

		account_numbers.append(account_number)
		custodian=random.choice(custodians)

		household,billing_group,fee_structure=sample_household_billing_group_fees()

		account = Account(name=name,account_number=account_number,custodian=custodian,opening_date=date,balance=balance, household=household,billing_group=billing_group,fee_structure=fee_structure)
		db.session.add(account)
	

if __name__ == '__main__':
	generate_fee_structures()
	generate_households()
	generate_billing_groups()
	generate_accounts()
	db.session.commit()