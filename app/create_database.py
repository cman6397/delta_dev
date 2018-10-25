#from tests import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)

app.config['SECRET_KEY']='45968594lkjgnf24958caskcturoty234'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///data_base/Billing_Data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), unique=False, nullable=False)

	def __repr__(self):
		return '<username = %r, password= %r>' % (self.username, self.password)

class Fee_Structure(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	collection=db.Column(db.String(100), unique=False, nullable=False)
	structure=db.Column(db.String(100), unique=False, nullable=False)
	flat_rate=db.Column(db.Numeric(precision=4), unique=False, nullable=True)
	flat_fee=db.Column(db.Numeric(precision=2), unique=False, nullable=True)
	valuation_method=db.Column(db.String(100), unique=False, nullable=False)
	frequency=db.Column(db.String(100), unique=False, nullable=False)
	quarterly_cycle=db.Column(db.String(100), unique=False, nullable=True)
	accounts = db.relationship('Account', backref='fee_structure', lazy='dynamic')

	def __repr__(self):
		return '<id = %r, name= %r>' % (self.id, self.name)

class Household(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	accounts = db.relationship('Account', backref='household', lazy='dynamic')
	billing_group = db.relationship('Billing_Group', back_populates='billing_group', uselist=False)

	def __repr__(self):
		return '<id = %r, name = %r>' % (self.id,self.name)

class Billing_Group(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	household_id=db.Column(db.Integer,db.ForeignKey(Household.id, ondelete='SET NULL'), nullable=True)
	accounts = db.relationship('Account', back_populates='billing_group')
	household= db.relationship('Household', back_populates="household")
	
	def __repr__(self):
		return '<id = %r, name= %r>' % (self.id, self.name)

Account_Split = db.Table('Account_Split',
    db.Column('Account_id', db.Integer, db.ForeignKey('account.id')),
    db.Column('Split_id', db.Integer, db.ForeignKey('split.id'))
)

class Split(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	splitter=db.Column(db.String(100), unique=False, nullable=False)
	split_percentage=db.Column(db.Numeric(precision=4), unique=False, nullable=True)

	def __repr__(self):
		return '<id = %r, name= %r>' % (self.id, self.name)

class Account(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	account_number=db.Column(db.Integer, unique=True, nullable=False)
	name = db.Column(db.String(500), unique=False, nullable=True)
	custodian = db.Column(db.String(100), unique=False, nullable=True)
	opening_date = db.Column(db.Date(), unique=False, nullable=True)
	balance=db.Column(db.Numeric(precision=2), unique=False, nullable=True)
	payment_source = db.Column(db.String(100), unique=False, nullable=True)
	household_id= db.Column(db.Integer, db.ForeignKey(Household.id, ondelete='SET NULL'), nullable=True)
	fee_id= db.Column(db.Integer, db.ForeignKey(Fee_Structure.id, ondelete='SET NULL'), nullable=True)
	billing_group_id= db.Column(db.Integer, db.ForeignKey(Billing_Group.id, ondelete='SET NULL'), nullable=True)
	billing_group= db.relationship("Billing_Group", back_populates="accounts")
	fee_location_id = db.Column(db.Integer, db.ForeignKey(id, ondelete='SET NULL'), nullable=True)
	fee_location = db.relationship("Account", backref='accounts', remote_side=[id])
	splits = db.relationship("Split", secondary=Account_Split, backref=db.backref('accounts'))
	history = db.relationship('Account_History', back_populates='account')

	def __repr__(self):
		return '<id = %r, name = %r, account_number= %r, custodian= %r, opening_date= %r, balance= %r>' % (self.id, self.name, self.account_number,self.custodian,self.opening_date,self.balance)

class Account_History(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	account_id= db.Column(db.Integer, db.ForeignKey(Account.id), nullable=False)
	account = db.relationship("Account", back_populates="history")
	date = db.Column(db.Date(), unique=False, nullable=True)
	balance=db.Column(db.Numeric(precision=2), unique=False, nullable=True)

db.create_all()