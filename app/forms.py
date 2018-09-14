from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
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

class Fee_StructureForm(FlaskForm):
	name= StringField('Fee Structure', validators=[DataRequired()])
	frequency=SelectField('Frequencies', choices = [(1, '---'),(2, 'Monthly'), (3, 'Quarterly')], default=1)
	collection=SelectField('Collection Options', choices=[(1, '---'),(2,'Advance with Proration'), (3,'Arrears'),(4,'Advance')], default=1)
	structure=SelectField('Fee Structures', choices=[(1, '---'),(2,'Flat Rate'),(3,'Flat Fee'),(4,'Favor')], default=1)
	valuation_method=SelectField('Valuation Methods', choices=[(1, '---'),(2,'Ending Period balance'),(3,'Average Daily Balance')], default=1)

	submit = SubmitField('Create Fee Structure')





		


