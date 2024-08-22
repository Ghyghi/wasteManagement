from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, SubmitField, IntegerField, DateTimeField, EmailField
from wtforms.validators import DataRequired, Email, Length, InputRequired, ValidationError

roles = [
    ('Collector' , 'Collector'),
    ('Household' , 'Household')
]

days_of_the_week = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday')
]

districts =[
    ('Gasabo', 'Gasabo'),
    ('Kicukiro', 'Kicukiro'),
    ('Nyarugenge', 'Nyarugenge')
]

gasabo_sectors = [
    ('Gisozi', 'Gisozi'),
    ('Kacyiru', 'Kacyiru'),
    ('Kimironko', 'Kimironko'),
    ('Remera', 'Remera')
]

kicukiro_sectors = [
    ('Gikondo', 'Gikondo'),
    ('Kanombe', 'Kanombe'),
    ('Kicukiro', 'Kicukiro')
]

nyarugenge_sectors = [
    ('Muhima', 'Muhima'),
    ('Nyamirambo', 'Nyamirambo'),
    ('Kimisagara', 'Kimisagara')
]
freq = [('Monthly', 'Monthly'), ('Weekly', 'Weekly')]
sectors = gasabo_sectors + kicukiro_sectors + nyarugenge_sectors
class AdminRegisterForm(FlaskForm):
    companyname = StringField('Company Name', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    email = EmailField('Email', validators=[InputRequired()])
    submit = SubmitField('Register')
class AdminLoginForm(FlaskForm):
    companyname = StringField('Company Name', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    submit = SubmitField('Login')
class HouseRegisterForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired()])
    secondname = StringField("Second Name", validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    email = EmailField('Email', validators=[InputRequired()])
    submit = SubmitField('Register')
class HouseLoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    submit = SubmitField('Login')
class VerifyEmailForm(FlaskForm):
    otp = StringField('Verify your email', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')
class ResendConfirmationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Confirmation Email')
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    submit = SubmitField('Reset Password')
class RoutesForm(FlaskForm):
    company = IntegerField('Company ID', validators=[InputRequired()])
    days = SelectField('Pickup Day', choices=days_of_the_week, validators=[InputRequired()])
    district = SelectField('Choose District', choices=districts, validators=[InputRequired()])
    sector = SelectField('Choose Sector', choices=sectors, validators=[InputRequired()])
    frequency = SelectField('Pickup Frequency', choices=freq, validators=[InputRequired()])
    submit = SubmitField('Register Route')
class UpdateRouteForm(FlaskForm):
    pickup_days = SelectField('Pickup Day', choices=days_of_the_week, validators=[InputRequired()])
    frequency = SelectField('Pickup Frequency', choices=freq, validators=[InputRequired()])
    submit = SubmitField('Update Route')

class CollectorRegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired()])
    secondname = StringField('Second Name', validators=[InputRequired()])
    companyname = StringField('Company Name', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired(), Length(min=8, max=50)])
    collectoremail = EmailField('Your email', validators=[InputRequired()])
    submit = SubmitField('Register')