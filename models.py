from flask_login import UserMixin
from extensions import db
import jwt
import os
from time import time
from datetime import date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,nullable=False)
    email = db.Column(db.String(50), unique=True,nullable=False)
    password = db.Column(db.String(255), nullable=False)
    f_name = db.Column(db.String(20),nullable=False)
    l_name = db.Column(db.String(20),nullable=False)
    dAge = db.Column(db.Integer,nullable=False)
    ddbirth = db.Column(db.Date,nullable=False)
    dSex = db.Column(db.String(6), nullable=False)
    patients = db.relationship('Patient', backref='user')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    

    def __repr__(self):
        return 'User {}'.format(self.username)

    def get_reset_token(self, expires=990):
        return jwt.encode(
            {'reset_password': self.username, 'exp': time() + expires},
            os.getenv('SECRET_KEY', 'random_key'), algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            username = jwt.decode(token, os.getenv('SECRET_KEY', 'random_key'),
                                  algorithm='HS256')['reset_password']
        except:
            return
        return User.query.filter_by(username=username).first()

    @staticmethod
    def verify_email(email):
        user = User.query.filter_by(email=email).first()
        return user


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fName = db.Column(db.String(20), nullable=False)
    pAge = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(6), nullable=False)
    diagnosis = db.Column(db.String(30), nullable=False,default='Not Diagnosed Yet')
    lName = db.Column(db.String(20), nullable=False)
    patientEmail = db.Column(db.String(50), nullable=True)
    dbirth = db.Column(db.Date, nullable=False)
    doctor_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

    def __repr__(self):
        return 'Patient {}'.format(self.patientUsername)

    def get_reset_token(self, expires=990):
        return jwt.encode(
            {'reset_password': self.patientUsername, 'exp': time() + expires},
            os.getenv('SECRET_KEY', 'random_key'), algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            patientUsername = jwt.decode(token, os.getenv('SECRET_KEY', 'random_key'),
                                  algorithm='HS256')['reset_password']
        except:
            return
        return Patient.query.filter_by(patientUsername=patientUsername).first()

    @staticmethod
    def verify_email(email):
        patient = Patient.query.filter_by(patientEmail=email).first()
        return patient



class Admin(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    adminFirstName = db.Column(db.String(20), nullable=False)
    adminLastName = db.Column(db.String(20), nullable=False)
    adminUsername = db.Column(db.String(20), nullable=False, unique=True)
    adminPassword = db.Column(db.String(30), nullable=False)
    adminEmail= db.Column(db.String(50), unique=True,nullable=False)
    doctors = db.relationship('User', backref='admin')

    def __repr__(self):
        return 'Admin {}'.format(self.adminUsername)

    def get_reset_token(self, expires=990):
        return jwt.encode(
            {'reset_password': self.adminUsername, 'exp': time() + expires},
            os.getenv('SECRET_KEY', 'random_key'), algorithm='HS256')

    @staticmethod
    def verify_reset_token(token):
        try:
            adminUsername = jwt.decode(token, os.getenv('SECRET_KEY', 'random_key'),
                                  algorithm='HS256')['reset_password']
        except:
            return
        return Admin.query.filter_by(adminUsername=adminUsername).first()

    @staticmethod
    def verify_email(email):
        admin = Admin.query.filter_by(adminEmail=email).first()
        return admin