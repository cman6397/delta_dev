import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'very very secret'
	sQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///data_base/Billing_Data.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
