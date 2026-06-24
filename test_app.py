import unittest
import os
import json
import database

# Force database path to a test database file before app initialization
database.DATABASE = os.path.join(os.path.dirname(__file__), 'test_students.db')

from app import app
from database import init_db

class StudentRegistrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize test database and seed entries
        init_db(force_seed=True)
        app.config['TESTING'] = True
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        # Remove test database file
        if os.path.exists(database.DATABASE):
            os.remove(database.DATABASE)

    def test_1_seed_data(self):
        """Verifies that seed data is successfully initialized."""
        # Log in admin using session transaction
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'
        
        response = self.client.get('/students')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 2)

    def test_2_valid_registration(self):
        """Verifies that a valid registration succeeds and returns a sequential ID."""
        payload = {
            "first_name": "Test",
            "last_name": "Student",
            "email": "test.student@example.com",
            "phone": "01555555555",
            "date_of_birth": "2000-01-01",
            "gender": "Other",
            "address": "789 Test Lane",
            "course_name": "Data Science & AI"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['registration_id'], 'REG1003')

    def test_3_duplicate_email(self):
        """Verifies that registration fails when using an email already registered."""
        payload = {
            "first_name": "Another",
            "last_name": "Student",
            "email": "test.student@example.com", # duplicate
            "phone": "01555555556",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "address": "789 Test Lane",
            "course_name": "Computer Science"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('email', data['errors'])
        self.assertEqual(data['errors']['email'], "Email is already registered.")

    def test_4_duplicate_phone(self):
        """Verifies that registration fails when using a phone number already registered."""
        payload = {
            "first_name": "Another",
            "last_name": "Student",
            "email": "unique.student@example.com",
            "phone": "01555555555", # duplicate from test 2
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "address": "789 Test Lane",
            "course_name": "Computer Science"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('phone', data['errors'])
        self.assertEqual(data['errors']['phone'], "Phone number is already registered.")

    def test_5_underage_validation(self):
        """Verifies that a student must be at least 16 years old."""
        payload = {
            "first_name": "Young",
            "last_name": "Child",
            "email": "young.child@example.com",
            "phone": "01999999999",
            "date_of_birth": "2020-01-01", # 6 years old in 2026
            "gender": "Female",
            "address": "Playground St",
            "course_name": "Computer Science"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('date_of_birth', data['errors'])
        self.assertEqual(data['errors']['date_of_birth'], "Student must be at least 16 years old.")

    def test_6_phone_length_validation(self):
        """Verifies that the phone number must be exactly 11 digits."""
        payload = {
            "first_name": "Short",
            "last_name": "Phone",
            "email": "short.phone@example.com",
            "phone": "12345", # invalid length
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "address": "Phone St",
            "course_name": "Computer Science"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('phone', data['errors'])
        self.assertEqual(data['errors']['phone'], "Phone number must be exactly 11 digits (numbers only).")

    def test_7_name_format_validation(self):
        """Verifies that name fields can only contain alphabetical characters."""
        payload = {
            "first_name": "John123", # contains numbers
            "last_name": "Doe",
            "email": "john.number@example.com",
            "phone": "01722222222",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "address": "123 Main St",
            "course_name": "Computer Science"
        }
        response = self.client.post('/students', json=payload)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('first_name', data['errors'])
        self.assertEqual(data['errors']['first_name'], "Name must contain only alphabetic characters and spaces.")

    def test_8_status_transition_and_audit(self):
        """Verifies status workflow limits and historical logging."""
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'

        # Check initial state for REG1001 (student ID 1, status Submitted)
        response = self.client.get('/students/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['student']['status'], 'Submitted')
        self.assertEqual(len(data['history']), 1) # Only initial log in seed
        
        # Approve student
        approve_resp = self.client.put('/students/1/approve', json={"remarks": "Credentials checked out"})
        self.assertEqual(approve_resp.status_code, 200)
        
        # Verify status and history changes
        response = self.client.get('/students/1')
        data = json.loads(response.data)
        self.assertEqual(data['student']['status'], 'Approved')
        self.assertEqual(len(data['history']), 2)
        self.assertEqual(data['history'][0]['new_status'], 'Approved')
        self.assertEqual(data['history'][0]['remarks'], 'Credentials checked out')

        # Try to reject an already approved application (must fail)
        reject_resp = self.client.put('/students/1/reject', json={"remarks": "Change mind"})
        self.assertEqual(reject_resp.status_code, 400)
        
        # Try to approve it again (must fail)
        approve_again = self.client.put('/students/1/approve', json={"remarks": "Double approve"})
        self.assertEqual(approve_again.status_code, 400)

    def test_9_public_tracker(self):
        """Verifies student status tracker queries."""
        # Find by ID
        response = self.client.get('/students/track?query=REG1002')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['first_name'], 'Jane')
        self.assertEqual(data['status'], 'Approved')

        # Find by Email
        response2 = self.client.get('/students/track?query=jane.smith@example.com')
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        self.assertEqual(data2['registration_id'], 'REG1002')

        # Search non-existent
        response_fail = self.client.get('/students/track?query=REG9999')
        self.assertEqual(response_fail.status_code, 404)

if __name__ == '__main__':
    unittest.main()
