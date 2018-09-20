from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional
from app.models import User,Household

class DollarField(DecimalField):
    def process_formdata(self, valuelist):
        if len(valuelist) == 1:
            self.data = [valuelist[0].strip('$').replace(',', '')]
        else:
            self.data = []


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
	name= StringField('Name', validators=[DataRequired()],render_kw={"placeholder": "Enter Structure Name","class": "form-control"})
	collection=SelectField('Collection', choices=[(1, '---'),('Advance with Proration','Advance with Proration'), ('Arrears','Arrears'),('Advance','Advance')], default=1,render_kw={"class": "custom-select mr-sm-1"})
	structure=SelectField('Fee Structure', choices=[(1, '---'),('Flat Rate','Flat Rate'),('Flat Fee','Flat Fee'),('Favor','Favor')], default=1,render_kw={"class": "custom-select mr-sm-1"})
	flat_rate = DecimalField('Fee Rate (%)', places=2, number_format='{0:.2f}%',validators=[Optional()],render_kw={"placeholder": "e.g., 0.5","class": "hidden"})
	flat_fee= DollarField('Annual Amount ($)', places=2,validators=[Optional()],render_kw={"placeholder": "e.g., 1500","class": "hidden"})
	valuation_method=SelectField('Valuation Method', choices=[(1, '---'),('Ending Period balance','Ending Period balance'),('Average Daily Balance','Average Daily Balance')], default=1,render_kw={"class": "custom-select mr-sm-1"})
	frequency=SelectField('Frequency', choices = [(1, '---'),('Monthly', 'Monthly'), ('Quarterly', 'Quarterly')], default=1,render_kw={"class": "custom-select mr-sm-1", "id":"frequency"})
	quarterly_cycle=SelectField('Quarterly Cycle', choices=[(1, '---'),('Mar-Jun-Sep-Dec','Mar-Jun-Sep-Dec'),('Feb-May-Aug-Nov','Feb-May-Aug-Nov'),('Jan-Apr-Jul-Oct','Jan-Apr-Jul-Oct')], default=1,validators=[Optional()],render_kw={"class": "hidden custom-select mr-sm-1", "id":"quarterly_cycle"})
	submit = SubmitField('Create Fee Structure')





		


