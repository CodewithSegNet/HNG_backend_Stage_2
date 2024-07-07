import uuid
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
import re
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey





def validate_fields(data):
    """
    A helper function that validates user fields based on data.
    """
    errors = []

    # Validate firstName
    if 'firstName' not in data or not data['firstName'] or len(data['firstName']) > 255 or not data['firstName'].isalpha():
        errors.append({
            "field": "firstName",
            "message": "First name must be provided, less than 255 characters, and contain only alphabetic characters."
        })

    # Validate lastName
    if 'lastName' not in data or not data['lastName'] or len(data['lastName']) > 255 or not data['lastName'].isalpha():
        errors.append({
            "field": "lastName",
            "message": "Last name must be provided, less than 255 characters, and contain only alphabetic characters."
        })

    # Validate email format
    if 'email' not in data or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
        errors.append({
            "field": "email",
            "message": "Invalid email format."
        })

    # Validate password length
    if 'password' not in data or not data['password'] or len(data['password']) < 5:
        errors.append({
            "field": "password",
            "message": "Password must be at least 5 characters long."
        })

    # Validate phone number format (adjust regex according to your requirements)
    if 'phone' not in data or not re.match(r'^\+?[0-9]+$', data['phone']):
        errors.append({
            "field": "phone",
            "message": "Invalid phone number format."
        })

    return errors


class User(db.Model):
    """
    A class that defines the User Table/Credentials 
    """
    __tablename__ = 'users'
    userId = db.Column(db.String(255), primary_key=True, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    firstName = db.Column(db.String(255), nullable=False)
    lastName = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    organisation_id = db.Column(db.String(255), db.ForeignKey('organisations.orgId'), nullable=True)



    def __init__(self, firstName, lastName, email, password, phone, organisation_id=None):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.phone = phone
        self.organisation_id = organisation_id


        self.validate_fields()


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


    def validate_fields(self):
        """
        A method that validates user fields.
        """
        errors = validate_fields({
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'password': self.password,
            'phone': self.phone
        })

        if errors:
            raise ValueError(errors)

    def __repr__(self):
        return f"<User {self.userId}, {self.firstName}, {self.lastName}, {self.email}, {self.phone}>"



    
        



