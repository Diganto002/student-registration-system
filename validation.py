import re
from datetime import datetime, date
from database import query_db

def validate_name(name):
    """Validates that a name is 2-50 characters, containing only letters and spaces."""
    if not name:
        return "Name is required."
    name = name.strip()
    if len(name) < 2 or len(name) > 50:
        return "Name must be between 2 and 50 characters."
    if not re.match(r"^[A-Za-z\s]+$", name):
        return "Name must contain only alphabetic characters and spaces."
    return None

def validate_email(email, student_id=None):
    """Validates email format and ensures uniqueness in the database."""
    if not email:
        return "Email is required."
    email = email.strip().lower()
    if len(email) > 100:
        return "Email must be less than 100 characters."
    # Standard email regex pattern
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return "Invalid email format."
    
    # Uniqueness check
    if student_id:
        existing = query_db("SELECT id FROM students WHERE email = ? AND id != ?", (email, student_id), one=True)
    else:
        existing = query_db("SELECT id FROM students WHERE email = ?", (email,), one=True)
        
    if existing:
        return "Email is already registered."
    return None

def validate_phone(phone, student_id=None):
    """Validates that phone is exactly 11 digits and is unique."""
    if not phone:
        return "Phone number is required."
    phone = phone.strip()
    if not re.match(r"^\d{11}$", phone):
        return "Phone number must be exactly 11 digits (numbers only)."
    
    # Uniqueness check
    if student_id:
        existing = query_db("SELECT id FROM students WHERE phone = ? AND id != ?", (phone, student_id), one=True)
    else:
        existing = query_db("SELECT id FROM students WHERE phone = ?", (phone,), one=True)
        
    if existing:
        return "Phone number is already registered."
    return None

def validate_dob(dob_str):
    """Validates date of birth: must be a valid past date and age must be at least 16."""
    if not dob_str:
        return "Date of Birth is required."
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid Date of Birth format. Use YYYY-MM-DD."
    
    today = date.today()
    if dob >= today:
        return "Date of Birth must be a past date."
        
    # Calculate age
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 16:
        return "Student must be at least 16 years old."
    return None

def validate_gender(gender):
    """Validates gender value."""
    if not gender:
        return "Gender is required."
    if gender not in ["Male", "Female", "Other"]:
        return "Gender must be Male, Female, or Other."
    return None

def validate_address(address):
    """Validates address length."""
    if not address:
        return "Address is required."
    address = address.strip()
    if len(address) > 255:
        return "Address must not exceed 255 characters."
    return None

def validate_course(course):
    """Validates course name length."""
    if not course:
        return "Course Name is required."
    course = course.strip()
    if len(course) > 100:
        return "Course Name must not exceed 100 characters."
    return None

def validate_registration_data(data, student_id=None):
    """Validates all student registration fields and returns dict of errors."""
    errors = {}
    
    first_name_err = validate_name(data.get('first_name'))
    if first_name_err: errors['first_name'] = first_name_err
        
    last_name_err = validate_name(data.get('last_name'))
    if last_name_err: errors['last_name'] = last_name_err
        
    email_err = validate_email(data.get('email'), student_id)
    if email_err: errors['email'] = email_err
        
    phone_err = validate_phone(data.get('phone'), student_id)
    if phone_err: errors['phone'] = phone_err
        
    dob_err = validate_dob(data.get('date_of_birth'))
    if dob_err: errors['date_of_birth'] = dob_err
        
    gender_err = validate_gender(data.get('gender'))
    if gender_err: errors['gender'] = gender_err
        
    address_err = validate_address(data.get('address'))
    if address_err: errors['address'] = address_err
        
    course_err = validate_course(data.get('course_name'))
    if course_err: errors['course_name'] = course_err
        
    return errors
