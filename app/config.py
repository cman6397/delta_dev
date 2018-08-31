import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY='45968594lkjgnf24958caskcturoty234'
	SQLALCHEMY_DATABASE_URI= 'sqlite:///data_base/Billing_Data.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
