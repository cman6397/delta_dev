from app import db
from flask_login import UserMixin
from app import login
from passlib.hash import sha256_crypt

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), unique=False, nullable=False)

	def set_password(self, password):
		self.password = sha256_crypt.hash(password)

	def check_password(self, password):
		return sha256_crypt.verify(password,self.password)

	@login.user_loader
	def load_user(id):
		return User.query.get(int(id))

	def __repr__(self):
		return '<username = %r, password= %r>' % (self.username, self.password)

class Fee_Structure(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	frequency=db.Column(db.String(100), unique=False, nullable=False)
	collection=db.Column(db.String(100), unique=False, nullable=False)
	structure=db.Column(db.String(100), unique=False, nullable=False)
	valuation_method=db.Column(db.String(100), unique=False, nullable=False)

	def __repr__(self):
		return '<id = %r, name= %r>' % (self.id, self.name)

class Household(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(500), unique=True, nullable=False)
	fee_id= db.Column(db.Integer, db.ForeignKey(Fee_Structure.id, ondelete='SET NULL'), nullable=True)
	accounts = db.relationship('Account', backref='household', lazy='dynamic')

	def __repr__(self):
		return '<id = %r, name= %r>' % (self.id, self.name)

class Account(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	account_number=db.Column(db.Integer, unique=True, nullable=False)
	name = db.Column(db.String(500), unique=False, nullable=True)
	custodian = db.Column(db.String(100), unique=False, nullable=True)
	opening_date = db.Column(db.Date(), unique=False, nullable=True)
	balance=db.Column(db.Numeric(precision=2), unique=False, nullable=True)
	household_id= db.Column(db.Integer, db.ForeignKey(Household.id, ondelete='SET NULL'), nullable=True)
	
	def __repr__(self):
		return '<id = %r, name = %r, account_number= %r, custodian= %r, opening_date= %r, balance= %r>' % (self.id, self.name, self.account_number,self.custodian,self.opening_date,self.balance)
