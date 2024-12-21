from idlelib.query import Query

from email_validator import validate_email
from flask_wtf import FlaskForm
from musician_select.models import User
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class RegisterForm(FlaskForm):

    def validate_email(self,email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Please enter a unique email address.')

    def validate_username(self,username_to_check):
        username = User.query.filter_by(username=username_to_check.data).first()
        if username:
            raise ValidationError('Please enter a unique username.')

    username = StringField(label='Username:',validators=[Length(4,30),DataRequired()])
    email = StringField(label='Email:',validators=[DataRequired(),Email(),])
    password1 = PasswordField(label='Password:',validators=[DataRequired(),Length(6,30)])
    password2 = PasswordField(label='Confirm Password:',validators=[DataRequired(),EqualTo('password1',message='Passwords must match')])
    submit = SubmitField(label='Register')

class LoginForm(FlaskForm):
    def validate_email(self, email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email is None:
            raise ValidationError("User with that email hasn't been registered.")

    email = StringField(label='Email:',validators=[DataRequired(),Email(),])
    password = PasswordField(label='Password:',validators=[DataRequired(),Length(6,30)],)
    submit = SubmitField(label='Sign in')
