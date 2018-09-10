from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from app.models import User,Household

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

	def verify_user(self):
		message="Invalid Username or Password"
		verified=False
		user = User.query.filter_by(username=self.username.data).first()
		if user and user.check_password(self.password.data):
			verified=True
			message="Login Successful"

		return verified, message, user

class HouseholdForm(FlaskForm):
	name= StringField('Household', validators=[DataRequired()])
	accounts = PasswordField('Accounts')
	submit = SubmitField('Create Household')

		


