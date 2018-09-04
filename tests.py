from flask import render_template,url_for,redirect,flash
from flask_login import current_user, login_user
from app import app
from app import db
from app.forms import LoginForm
from app.models import User
from passlib.hash import sha256_crypt

def create_user(username,password):
	registered=False
	message = "Username Taken"
	user = User.query.filter_by(username=username).first()
	if not user:
		user = User(username=username,password=password)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		message="User Registered"
		registered=True
	return registered,message

def remove_user(username):
	User.query.filter_by(username=username).delete()
	db.session.commit()

def show_table():
	table = User.query.all()
	for row in table:
		print(row)
		print(row.username, row.password)

def login_user(username,password):
	logged_in = False
	message="Invalid username or password."
	user = User.query.filter_by(username=username).first()
	if user and user.check_password(password):
		logged_in = True
		message="Login Successful"

	return logged_in, message

if __name__ == '__main__':
	username='admin'
	password='1234'

	remove_user(username)

	status,msg = create_user(username,password)
	assert status
	print(msg)

	status,msg = login_user(username,password)
	assert status
	print(msg)

	show_table()




