from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional, Length, InputRequired, NumberRange
from app.models import User,Household

class DollarField(DecimalField):
    def process_formdata(self, valuelist):
        if len(valuelist) == 1:
            self.data = float((valuelist[0].strip('$').replace(',', '')))
        else:
            self.data = None
class PercentField(DecimalField):
    def process_formdata(self, valuelist):
        if len(valuelist) == 1:
            self.data = float((valuelist[0].strip('%')))/100
        else:
            self.data = None


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired(),Length(max=50)])
	password = PasswordField('Password', validators=[InputRequired(),Length(max=50)])
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
	name= StringField('Name',render_kw={"placeholder": "Enter Structure Name","class": "form-control"}, default='', validators=[InputRequired(),Length(max=100)])
	collection=SelectField('Collection', choices=[('', '---'),('Advance with Proration','Advance with Proration'), ('Arrears','Arrears'),('Advance','Advance')], default='',render_kw={"class": "custom-select mr-sm-1"}, validators=[InputRequired()])
	structure=SelectField('Fee Structure', choices=[('', '---'),('Flat Rate','Flat Rate'),('Flat Fee','Flat Fee'),('Favor','Favor')],default='',render_kw={"class": "custom-select mr-sm-1"}, validators=[InputRequired()])
	flat_rate = PercentField('Fee Rate (%)', places=2,render_kw={"placeholder": "e.g., 0.5","class": "form-control"}, validators=[Optional(),NumberRange(max=100, min=0)])
	flat_fee= DollarField('Annual Amount ($)', places=2,render_kw={"placeholder": "e.g., $1,500","class": "form-control"}, validators=[Optional(),NumberRange(min=1)])
	valuation_method=SelectField('Valuation Method', choices=[('', '---'),('Ending Period Balance','Ending Period Balance'),('Average Daily Balance','Average Daily Balance')], default='',render_kw={"class": "custom-select mr-sm-1"}, validators=[InputRequired()])
	frequency=SelectField('Frequency', choices = [('', '---'),('Monthly', 'Monthly'), ('Quarterly', 'Quarterly')],default='',render_kw={"class": "custom-select mr-sm-1", "id":"frequency"}, validators=[InputRequired()])
	quarterly_cycle=SelectField('Quarterly Cycle', choices=[('', '---'),('Mar-Jun-Sep-Dec','Mar-Jun-Sep-Dec'),('Feb-May-Aug-Nov','Feb-May-Aug-Nov'),('Jan-Apr-Jul-Oct','Jan-Apr-Jul-Oct')],default='',render_kw={"class": "custom-select mr-sm-1", "id":"quarterly_cycle"}, validators=[Optional()])
	submit = SubmitField('Save')

class Billing_GroupForm(FlaskForm):
	name= StringField('Billing Group Name',render_kw={"placeholder": "Enter Billing Group Name","class": "form-control", "size": "30"}, default='', validators=[InputRequired(),Length(max=100)])
	submit = SubmitField('Save')

class SplitForm(FlaskForm):
	name= StringField('Name',render_kw={"placeholder": "Enter Split Name","class": "form-control", "size": "30"}, default='', validators=[InputRequired(),Length(max=100)])
	splitter= StringField('Splitter',render_kw={"placeholder": "Enter Splitter Name ","class": "form-control", "size": "30"}, default='', validators=[InputRequired(),Length(max=100)])
	split_percentage= PercentField('Split Percentage (%)', places=2,render_kw={"placeholder": "e.g., 20.0%","class": "form-control"}, validators=[Optional(),NumberRange(max=100, min=0)])
	submit = SubmitField('Save')

class Account_DetailsForm(FlaskForm):
    fee_location = SelectField('Fee Location', coerce=int, validators=[InputRequired()])
    payment_source=SelectField('Payment Source', choices = [('Directly Billed', 'Directly Billed'), ('Custodian Billed', 'Custodian Billed')], validators=[InputRequired()])
    account_id=StringField('Account Id', validators=[InputRequired()])
    submit = SubmitField('Save')

class Add_AccountForm(FlaskForm):
    account_id = StringField('Account Id', validators=[InputRequired()])
    submit = SubmitField('Add Account')

class Remove_AccountForm(FlaskForm):
    account_id = StringField('Account Id', validators=[InputRequired()])
    submit = SubmitField('Remove')




		


