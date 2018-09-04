from app import app
from app import db
from app.models import Account, Household
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
		account = Account(name=name,account_number=account_number,custodian=custodian,opening_date=date,balance=balance)
		db.session.add(account)
	
	db.session.commit()

if __name__ == '__main__':
	generate_accounts()