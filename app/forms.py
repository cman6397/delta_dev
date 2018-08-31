from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

    def set_password(self, password):
        self.password_hash = sha256_crypt.encrypt(password)

    def check_password(self, password):
    	return sha256_crypt.verify(self.password_hash,password)
