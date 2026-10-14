from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange
from sqlalchemy import ForeignKey
from wtforms import StringField, PasswordField, BooleanField, validators, RadioField, SelectField, IntegerField, \
    DateField
from wtforms.validators import InputRequired, Email, Length,DataRequired,Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=30)])

class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email format'), Length(max=50)])

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=30),validators.EqualTo('confirmpass',message='Passwords must match')])
    confirmpass = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=8, max=30)])


class UpdateAccountForm(FlaskForm):
    f_name=StringField('First Name:',validators=[DataRequired(), Length(min=2, max=20)])
    l_name=StringField('Last Name:',validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username:',validators=[DataRequired(), Length(min=4, max=20)])
    ddbirth = DateField('Date of Birth:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=30),
    validators.EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password:  ', validators=[InputRequired(), Length(min=8, max=30)])


class AddPatient(FlaskForm):
    fName = StringField('First Name:',validators=[DataRequired(), Length(min=2, max=20)])
    lName = StringField( 'Last Name:',validators=[DataRequired(), Length(min=2, max=20)])
    patientEmail = StringField('Email (optional):',validators=[Optional(), Email(), Length(max=50)])
    sex = RadioField('Gender:', choices=[('female', 'Female'), ('male', 'Male')],validators=[DataRequired()])
    dbirth = DateField('Date of Birth:',validators=[DataRequired()])
    dropdown_list = [('MS', 'MS'),('Stroke', 'Stroke'), ('Not Diagnosed Yet', 'Not Diagnosed Yet')]
    diagnosis = SelectField('Diagnosis:',choices=dropdown_list,default='Not Diagnosed Yet',validators=[DataRequired()])


class UpdatePatient(FlaskForm):
    fname=StringField('First Name: ',validators=[DataRequired(), Length(min=2, max=20)])
    lname=StringField('Last Name: ',validators=[DataRequired(), Length(min=2, max=20)])
    dbirth=DateField('Date of Birth:',validators=[DataRequired()])
    dropdown_list = ['MS', 'Stroke', 'Not Diagnosed Yet']
    diagnosis = SelectField('Diagnosis: ', choices=dropdown_list, default=1)
    patientEmail = StringField(
        'Patient Email (optional):',
        validators=[Optional(), Email(), Length(max=50)]
    )


class RegisterDoctorForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=20)]
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)]
    )

    f_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=20)]
    )

    l_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=20)]
    )

    ddbirth = DateField(
        "Date of Birth",
        format="%Y-%m-%d",
        validators=[InputRequired()]
    )

    dSex = SelectField(
        "Gender",
        choices=[("Male", "Male"), ("Female", "Female")],
        validators=[InputRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=30)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo("password", message="Passwords must match.")
        ]
    )

    submit = SubmitField("Create Doctor Account")