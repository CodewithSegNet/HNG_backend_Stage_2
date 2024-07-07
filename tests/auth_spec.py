import unittest
from datetime import datetime, timedelta
from flask import current_app
import uuid
from app import app, db
from flask_jwt_extended import create_access_token
from models.users import User
import jwt
import logging



# Configure logging
logging.basicConfig(level=logging.DEBUG)

class TestTokenGeneration(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()  # Ensure all tables are created
        
        db.session.rollback()  # Rollback any existing transactions
        db.session.query(User).delete()  # Delete all existing users (if needed)

        # Create a new user for testing
        self.user = User(
            firstName='grace',
            lastName='Doe',
            email='john.doe@example.com',
            password='password123',
            phone='1234567890',
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()  
        db.session.remove()
        self.app_context.pop()

    def test_token_expiration(self):
        expiration_time = timedelta(hours=2)
        access_token = create_access_token(identity=str(self.user.userId))
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        token_exp = datetime.utcfromtimestamp(decoded_token['exp'])
        expected_exp = datetime.utcnow() + expiration_time
        self.assertLessEqual(token_exp, expected_exp)

    def test_token_contains_correct_user_details(self):
        access_token = create_access_token(identity=str(self.user.userId))
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        self.assertEqual(decoded_token['sub'], str(self.user.userId))


    def test_register_user_with_default_organisation(self):
        # Create a registration payload
        registration_data = {
            'firstName': 'Alice',
            'lastName': 'Smith',
            'email': 'alice.smith@example.com',
            'password': 'password123',
            'phone': '3838484938474'
        }

        # Make a POST request to register the user
        response = self.client.post('/auth/register', json=registration_data)

        # Log the response JSON if the status code is not 201
        if response.status_code != 201:
            logging.debug(f"Response JSON: {response.json}")

        # Assert the response status code
        self.assertEqual(response.status_code, 201, f"Expected status code 201, but got {response.status_code}")

        # Assert that the response contains the expected user details and access token
        self.assertIn('data', response.json, "Response does not contain 'data'")
        self.assertIn('user', response.json['data'], "Response does not contain 'user'")
        self.assertIn('accessToken', response.json['data'], "Response does not contain 'accessToken'")
        self.assertEqual(response.json['data']['user']['firstName'], 'Alice', "Incorrect 'firstName' in response")
        self.assertEqual(response.json['data']['user']['lastName'], 'Smith', "Incorrect 'lastName' in response")

        # Optionally, check database state after registration
        registered_user = User.query.filter_by(email='alice.smith@example.com').first()
        self.assertIsNotNone(registered_user, "User record not found in the database after registration")


    def test_login_user(self):
        login_data = {
            'email': 'alice.smith@example.com',
            'password': 'password123',
        }

        response = self.client.post('/auth/login', json=login_data)
        if response.status_code != 200:
            logging.debug(f"Login response: {response.json}")

        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.json['data'])
        self.assertIn('token', response.json['data'])
        self.assertEqual(response.json['data']['user']['email'], 'alice.smith@example.com')




    def test_missing_required_fields(self):
        required_fields = ['firstName', 'lastName', 'email', 'password', 'phone']

        for field in required_fields:
            registration_data = {
                'firstName': 'Alice',
                'lastName': 'Smith',
                'email': 'alice.smith@example.com',
                'password': 'password123',
                'phone': '468892837366'
            }
            del registration_data[field]  # Simulate missing a required field

            response = self.client.post('/auth/register', json=registration_data)

            self.assertEqual(response.status_code, 422)

            # Check if 'errors' is a list or a dictionary
            if isinstance(response.json['errors'], list):
                # Iterate over the list of errors
                field_found_in_errors = any(field.lower() in error.lower() for error in response.json['errors'])
            elif isinstance(response.json['errors'], dict):
                # If 'errors' is a dictionary, assume the missing field is the key
                field_found_in_errors = field.lower() in response.json['errors'].keys()
            else:
                # Handle unexpected response format
                self.fail(f"Unexpected format of 'errors' in response: {response.json['errors']}")

            self.assertTrue(field_found_in_errors, f"{field} not found in errors: {response.json['errors']}")





    def test_duplicate_email(self):
        registration_data = {
            'firstName': 'Alice',
            'lastName': 'Smith',
            'email': 'alice.smith@example.com',
            'password': 'password123',
        }

        response1 = self.client.post('/auth/register', json=registration_data)
        if response1.status_code != 200:
            logging.debug(f"First registration response: {response1.json}")

        self.assertEqual(response1.status_code, 200)

        response2 = self.client.post('/auth/register', json=registration_data)
        self.assertEqual(response2.status_code, 422)
        self.assertIn('email', response2.json['errors'].lower())




if __name__ == '__main__':
    unittest.main()
