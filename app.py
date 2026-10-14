from __future__ import division, print_function

from functools import wraps
from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify,Blueprint,session
from flask_bootstrap import Bootstrap
from flask_login_multi.login_manager import LoginManager
from flask_login_multi import login_user, login_manager
from wtforms.validators import Email 
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, logout_user,login_user,login_required,current_user 
from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm
from flask_mail import Mail, Message
from flask_session import Session
from time import time
from datetime import date
from extensions import db, login_manager, mail
import os
# coding=utf-8
import sys
import re
import numpy as np
from pathlib import Path
from models import User, Patient, Admin
from forms import *


# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# Model saved with Keras model.save()
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{DATABASE_PATH.as_posix()}"
)
MODEL_PATH = 'models\MSStrokeModelBestt.h5'
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db.init_app(app)


model = load_model(MODEL_PATH)
print('Model loaded. Start serving...')
file_path = os.path.abspath(os.getcwd())+"\database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME']=os.environ.get("MAIL_USERNAME")
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD']=os.environ.get("MAIL_PASSWORD")
bootstrap = Bootstrap(app)
login_manager.session_protection = 'strong'

login_manager = LoginManager(app)

login_manager.blueprint_login_views = {
        'user':  "user.user_login",
        'admin': "admin.admin_login",
        'patient': "patient.patient_login",
    }

admin_app = Blueprint('admin', __name__,url_prefix="/admin")
user_app = Blueprint('user', __name__,url_prefix="/user")
patient_app = Blueprint('patient', __name__,url_prefix="/patient")
mail=Mail(app)



@login_manager.user_loader
def load_user(id, endpoint='user'):
    if endpoint == 'admin':
        return Admin.query.get(id)
    elif endpoint == 'patient':
        return Patient.query.get(id)
    else:
        return User.query.get(id)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap



def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(300, 300)) #target_size must agree with what the trained model expects!!

    # Preprocessing the image
    #img = image.img_to_array(img)
   # img = np.expand_dims(img, axis=0)


    #preds = model.predict_classes(img)
    #return preds

    #img = image.resize((300, 300))


    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x, mode='tf')

    preds = model.predict(x)
    return preds



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        # Doctor login
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                session['logged_in'] = True
                login_user(user, remember=True)
                return redirect(url_for('patientlist', doctor_id=user.id))

        # Admin login
        admin = Admin.query.filter_by(adminUsername=username).first()

        if admin:
            if check_password_hash(admin.adminPassword, form.password.data):
                session['logged_in'] = True
                login_user(admin)
                return redirect(url_for('doctorlist', admin_id=admin.id))

        flash('Invalid username or password', 'alert alert-danger boxalert')

    return render_template('login.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterDoctorForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "alert alert-danger")
            return render_template("register.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "alert alert-danger")
            return render_template("register.html", form=form)
        dob = form.ddbirth.data
        today = date.today()

        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        doctor = User(
            username=username,
            email=email,
            password=generate_password_hash(form.password.data),
            f_name=form.f_name.data.strip(),
            l_name=form.l_name.data.strip(),
            dAge=age,
            ddbirth=form.ddbirth.data,
            dSex=form.dSex.data
        )

        try:
            db.session.add(doctor)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Doctor registration failed.")
            flash(
                "Unable to create the account. Please try again.",
                "alert alert-danger"
            )
            return render_template("register.html", form=form)

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


def send_email(user):
    token = user.get_reset_token()
    msg = Message()
    msg.subject = "Login System: Password Reset Request"
    msg.sender = 'nonreply@gmail.com'
    msg.recipients = [user.email]
    msg.html = render_template('reset_pwd.html', user=user, token=token)
    mail.send(msg)

def send_emailadmin(admin):
    token = admin.get_reset_token()
    msg = Message()
    msg.subject = "Login System: Password Reset Request"
    msg.sender = 'nonreply@gmail.com'
    msg.recipients = [admin.adminEmail]
    msg.html = render_template('reset_pwdadmin.html', admin=admin, token=token)
    mail.send(msg)

def send_emailpatient(patient):
    token = patient.get_reset_token()
    msg = Message()
    msg.subject = "Login System: Password Reset Request"
    msg.sender = 'nonreply@gmail.com'
    msg.recipients = [patient.patientEmail]
    msg.html = render_template('reset_pwd.html', patient=patient, token=token)
    mail.send(msg)

@app.route("/<int:doctor_id>/account/", methods=['GET', 'POST'])
@login_required
def account(doctor_id):
    form = UpdateAccountForm()
    user = User.query.get_or_404(doctor_id)
    if form.validate_on_submit():
        existsUsername = db.session.query(db.exists().where(User.username == form.username.data)).scalar()
        existsUsername3 = db.session.query(db.exists().where(Admin.adminUsername == form.username.data)).scalar()
        if (existsUsername or existsUsername3) and (current_user.username!=form.username.data):
            flash('This username is already taken.','alert alert-danger boxalert')
        else:
            hashed_password = generate_password_hash(form.password.data)
            current_user.f_name = form.f_name.data
            current_user.l_name = form.l_name.data
            current_user.username = form.username.data
            current_user.password = hashed_password
            dbir = form.ddbirth.data
            current_user.ddbirth=form.ddbirth.data
            today = date.today()
            dage = today.year - dbir.year - ((today.month, today.day) < (dbir.month, dbir.day))
            if dage < 21 or dage > 80:
                flash('Please select a valid age (21-80)', 'alert alert-danger boxalert')
            else:
                current_user.dAge=dage
                db.session.commit()
                flash('Your account has been updated!', 'success' )
                return redirect(url_for('account',doctor_id=user.id))
    elif request.method == 'GET':
        form.f_name.data = current_user.f_name
        form.l_name.data = current_user.l_name
        form.username.data = current_user.username
        form.ddbirth.data=current_user.ddbirth
        form.password.data = current_user.password
    return render_template('account.html', user=user, form=form)



def confirmationemail(doctor,password2):
   msg = Message('Your Account is Created Successfully ', sender = 'nonreply@gmail.com', recipients = [doctor.email])
   passw=str(password2)
   msg.html = render_template('confirmationemailadd.html', doctor=doctor,passw=passw,username=doctor.username)
   mail.send(msg)


def confirmationemailupdate(doctor):
   msg = Message('Account Update', sender = 'nonreply@gmail.com', recipients = [doctor.email])
   msg.body = "Your account has been updated successfully, please check the updated information in your system account"
   mail.send(msg)

def confirmationemailupdatepatient(patient):
    msg = Message('Account Update', sender='nonreply@gmail.com', recipients=[patient.patientEmail])
    msg.body = "Your account has been updated successfully, please check the updated information in your system account"
    mail.send(msg)



@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        admin = Admin.query.filter_by(adminEmail=form.email.data).first()
        patient = Patient.query.filter_by(patientEmail=form.email.data).first()
        if user:
            send_email(user)
            flash('Reset request sent. Check your email', 'alert alert-success boxalert')
            return redirect(url_for('login'))
        elif admin:
            send_emailadmin(admin)
            flash('Reset request sent. Check your email', 'alert alert-success boxalert')
            return redirect(url_for('login'))
        elif patient:
            send_emailpatient(patient)
            flash('Reset request sent. Check your email', 'alert alert-success boxalert')
            return redirect(url_for('login'))
        else:
            flash('This email address is not registered in this system', 'alert alert-danger boxalert')

    return render_template('reset.html', form=form)

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_verified(token):
    form=ResetPasswordForm()
    user = User.verify_reset_token(token)
    admin=Admin.verify_reset_token(token)
    patient = Patient.verify_reset_token(token)

    if form.validate_on_submit():
        if not user and not admin and not patient:
            flash('User not found or token has expired', 'alert alert-danger boxalert')
            return redirect(url_for('reset'))

        password = form.password.data

        if user and password:
            hashed_password = generate_password_hash(password)
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'alert alert-success boxalert')
            return redirect(url_for('login'))

        if admin and password:
            hashed_password = generate_password_hash(password)
            admin.adminPassword = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'alert alert-success boxalert')
            return redirect(url_for('login'))

        if patient and password:
            hashed_password = generate_password_hash(password)
            patient.patientPassword = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'alert alert-success boxalert')
            return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/<int:id>/<int:doctor_id>/')
@login_required
def mainpage(id,doctor_id):
    patient = Patient.query.get_or_404(id)
    user = User.query.get_or_404(doctor_id)
    session["patient_id"] = patient.id
    return render_template('mainpage.html', patient=patient,user=user)


@app.route('/<int:doctor_id>/patientlist/')
@login_required
def patientlist(doctor_id):
    user = User.query.get_or_404(doctor_id)
    return render_template('patientlist.html', user=user)


@app.route('/<int:doctor_id>/create/', methods=('GET', 'POST'))
@login_required
def create(doctor_id):
    form = AddPatient()
    user = User.query.get_or_404(doctor_id)

    if form.validate_on_submit():
        dbir = form.dbirth.data
        today = date.today()
        age = (
            today.year - dbir.year
            - ((today.month, today.day) < (dbir.month, dbir.day))
        )

        if age < 7 or age > 130:
            flash('Please select a valid age (7-130).','alert alert-danger')
        else:
            email = form.patientEmail.data
            if email:
                email = email.strip().lower()

            if email and Patient.query.filter_by(
                patientEmail=email
            ).first():
                flash('This email is already associated with a patient.','alert alert-danger')
            elif email and (
                User.query.filter_by(email=email).first()
                or Admin.query.filter_by(adminEmail=email).first()
            ):
                flash('This email is already in use.', 'alert alert-danger')
            else:
                patient = Patient(
                    fName=form.fName.data.strip(),
                    lName=form.lName.data.strip(),
                    pAge=age,
                    sex=form.sex.data,
                    diagnosis=form.diagnosis.data,
                    patientEmail=email,
                    dbirth=dbir,
                    doctor_id=user.id
                )

                db.session.add(patient)
                try:
                    db.session.commit()
                    flash('Patient added successfully.','success')
                    return redirect(url_for('patientlist', doctor_id=user.id))
                except Exception:
                    db.session.rollback()
                    app.logger.exception('Failed to create patient record')
                    flash('Unable to save the patient. Please try again.','alert alert-danger')

    return render_template('create.html',form=form,user=user)

@app.route(
    '/<int:id>/<int:doctor_id>/diagnosis-email-preview/',
    methods=['GET']
)

@app.route('/<int:id>/<int:doctor_id>/diagnosis-email-preview/', methods=['GET'])
@login_required
def diagnosis_email_preview(id, doctor_id):
    if current_user.id != doctor_id:
        abort(403)

    patient = Patient.query.get_or_404(id)

    if patient.doctor_id != doctor_id:
        abort(404)

    if not patient.patientEmail:
        return jsonify({'error': 'This patient has no saved email address.'}), 400

    if not patient.diagnosis:
        return jsonify({'error': 'This patient has no saved diagnosis.'}), 400

    return jsonify({
        'patient_name': f'{patient.fName} {patient.lName}',
        'recipient': patient.patientEmail,
        'diagnosis': patient.diagnosis
    })



@app.route('/<int:id>/<int:doctor_id>/send-diagnosis/', methods=['POST'])
@login_required
def send_diagnosis(id, doctor_id):
    if current_user.id != doctor_id:
        abort(403)

    patient = Patient.query.get_or_404(id)

    if patient.doctor_id != doctor_id:
        abort(404)

    recipient = request.form.get('recipient', '').strip()
    diagnosis = request.form.get('diagnosis', '').strip()

    if not recipient or not diagnosis:
        flash('Recipient email and diagnosis are required.', 'danger')
        return redirect(url_for('patientlist', doctor_id=doctor_id))

    from email_validator import validate_email, EmailNotValidError

    try:
        recipient = validate_email(
            recipient, check_deliverability=False
        ).normalized
    except EmailNotValidError:
        flash('Please enter a valid recipient email address.', 'danger')
        return redirect(url_for('patientlist', doctor_id=doctor_id))

    try:
        patient_name = f'{patient.fName} {patient.lName}'

        # The subject is predefined by the backend.
        subject = 'Your Medical Assessment Result'

        # The message is generated from the backend template.
        message_body = render_template(
            'emails/diagnosis_notification.txt',
            patient_name=patient_name,
            diagnosis=diagnosis
        )

        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=message_body,
            sender=app.config.get('MAIL_DEFAULT_SENDER') or 'nonreply@gmail.com'
        )

        mail.send(msg)

        flash('Diagnosis email sent successfully.', 'success')

    except Exception as e:
        app.logger.exception("Failed to send diagnosis email: %s", e)
        flash(
            'The email could not be sent. Check the Flask terminal for details.',
            'danger'
        )

    return redirect(url_for('patientlist', doctor_id=doctor_id))



@app.route('/<int:id>/<int:doctor_id>/edit/', methods=['GET', 'POST'])
@login_required
def patientupdate(id, doctor_id):
    form = UpdatePatient()
    patient = Patient.query.get_or_404(id)
    user = User.query.get_or_404(doctor_id)

    if form.validate_on_submit():
        dbir = form.dbirth.data
        today = date.today()

        age = (
            today.year - dbir.year
            - ((today.month, today.day) < (dbir.month, dbir.day))
        )

        if age < 7 or age > 130:
            flash(
                'Please select a valid age (7-130)',
                'alert alert-danger boxalert'
            )
        else:
            email = form.patientEmail.data
            email = email.strip().lower() if email else None
            existing_patient = Patient.query.filter(
                Patient.patientEmail == email,
                Patient.id != patient.id
            ).first() if email else None
            existing_user = User.query.filter_by(
                email=email
            ).first() if email else None

            existing_admin = Admin.query.filter_by(
                adminEmail=email
            ).first() if email else None

            if existing_patient or existing_user or existing_admin:
                flash(
                    'This email address is already in use.',
                    'alert alert-danger boxalert'
                )
            else:
                patient.fName = form.fname.data.strip()
                patient.lName = form.lname.data.strip()
                patient.pAge = age
                patient.dbirth = dbir
                patient.diagnosis = form.diagnosis.data
                patient.patientEmail = email

                try:
                    db.session.commit()
                    flash(
                        'Patient details updated successfully.',
                        'success'
                    )
                    return redirect(url_for(
                        'patientupdate',
                        id=patient.id,
                        doctor_id=user.id
                    ))
                except Exception:
                    db.session.rollback()
                    app.logger.exception('Failed to update patient')
                    flash(
                        'Unable to update patient details.',
                        'alert alert-danger boxalert'
                    )

    elif request.method == 'GET':
        form.fname.data = patient.fName
        form.lname.data = patient.lName
        form.dbirth.data = patient.dbirth
        form.diagnosis.data = patient.diagnosis
        form.patientEmail.data = patient.patientEmail

    return render_template(
        'patientupdate.html',
        patient=patient,
        user=user,
        form=form
    )

@app.route('/<int:id>/<int:doctor_id>/delete/',methods=["POST"])
@login_required
def delete(id,doctor_id):
    patient = Patient.query.get_or_404(id)
    user = User.query.get_or_404(doctor_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patientlist',doctor_id=user.id))

@app.route('/<int:admin_id>/doctorlist/')
@login_required
def doctorlist(admin_id):
    admin= Admin.query.get_or_404(admin_id)
    return render_template('doctorlist.html', admin=admin)



@app.route('/changepass')
@login_required
def changepass():
    doctors = User.query.all()
    return render_template('changepass.html', doctors=doctors)


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        f = request.files['file']


        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)



        pred_class = float("{:.5f}".format(np.argmax(preds)))
        # Process your result for human
        pred_proba = float("{:.3f}".format(np.amax(preds)))  # Max probability

        if pred_proba > 0.7:
            result = 'MS'
        else:
            result = 'Stroke'


        if "patient" in session:
            patient=session["patient"]
            patient.diagnosis=result
            db.session.add(patient)
            db.session.commit()


        return result



if __name__ == '__main__':
    app.run(debug=True)