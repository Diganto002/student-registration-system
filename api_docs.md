# Student Registration System - API Documentation

This API enables students to submit course registration applications and look up status, and enables administrators to view, filter, review (approve/reject), and export registration records.

## Authentication
Admin-only endpoints require a session-based cookie set via the admin login flow.
- **Login endpoint**: `POST /login` (Accepts form-data `username` and `password`)
- **Default Credentials**: `admin` / `admin123`

---

## Endpoint Specifications

### 1. Submit Registration
Creates a new course registration.

* **URL**: `/students`
* **Method**: `POST`
* **Headers**: `Content-Type: application/json`
* **Request Body Schema**:
  ```json
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "01712345678",
    "date_of_birth": "2005-05-15",
    "gender": "Male",
    "address": "123 Main St, Springfield",
    "course_name": "Computer Science"
  }
  ```
* **Validation Criteria**:
  * `first_name` & `last_name`: Required, 2-50 chars, alphabetic & spaces.
  * `email`: Required, valid email pattern, must be unique.
  * `phone`: Required, exactly 11 digits (numbers only), must be unique.
  * `date_of_birth`: Required, YYYY-MM-DD, age must be &ge; 16.
  * `gender`: Required, must be one of `Male`, `Female`, `Other`.
  * `address`: Required, max 255 characters.
  * `course_name`: Required, max 100 characters.

* **Response (Success - 201 Created)**:
  ```json
  {
    "success": true,
    "id": 3,
    "registration_id": "REG1003"
  }
  ```
* **Response (Validation Error - 400 Bad Request)**:
  ```json
  {
    "errors": {
      "phone": "Phone number must be exactly 11 digits (numbers only).",
      "date_of_birth": "Student must be at least 16 years old."
    }
  }
  ```

---

### 2. Search / List Registrations (Admin Only)
Retrieve student registrations with pagination, search, and status filtering.

* **URL**: `/students`
* **Method**: `GET`
* **Query Parameters**:
  * `limit` (optional): Integer (default `10`). Items to return.
  * `offset` (optional): Integer (default `0`). Starting offset.
  * `search` (optional): String. Search term matches `registration_id`, name, email, or phone.
  * `status` (optional): String. One of `Submitted`, `Approved`, `Rejected`.
* **Response (Success - 200 OK)**:
  ```json
  {
    "total": 2,
    "students": [
      {
        "id": 2,
        "registration_id": "REG1002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "01887654321",
        "date_of_birth": "2004-08-22",
        "gender": "Female",
        "address": "456 Oak Rd, Metropolis",
        "course_name": "Mechanical Engineering",
        "status": "Approved",
        "created_at": "2026-06-22 09:00:00"
      }
    ]
  }
  ```
* **Response (Unauthorized - 401 Unauthorized)**:
  ```json
  {
    "error": "Unauthorized admin access."
  }
  ```

---

### 3. Retrieve Single Registration Details (Admin Only)
Retrieve profile details and audit trail logs for a specific application.

* **URL**: `/students/<id>`
* **Method**: `GET`
* **Response (Success - 200 OK)**:
  ```json
  {
    "student": {
      "id": 2,
      "registration_id": "REG1002",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane.smith@example.com",
      "phone": "01887654321",
      "date_of_birth": "2004-08-22",
      "gender": "Female",
      "address": "456 Oak Rd, Metropolis",
      "course_name": "Mechanical Engineering",
      "status": "Approved",
      "created_at": "2026-06-22 09:00:00",
      "updated_at": "2026-06-22 11:30:00"
    },
    "history": [
      {
        "id": 3,
        "old_status": "Submitted",
        "new_status": "Approved",
        "changed_by": "Admin",
        "changed_at": "2026-06-22 11:30:00",
        "remarks": "Credentials and documents verified."
      },
      {
        "id": 2,
        "old_status": "None",
        "new_status": "Submitted",
        "changed_by": "System",
        "changed_at": "2026-06-22 09:00:00",
        "remarks": "Initial registration submission."
      }
    ]
  }
  ```

---

### 4. Approve Application (Admin Only)
Approve a submitted application. Transitions status to `Approved`. Can only transition from `Submitted`.

* **URL**: `/students/<id>/approve`
* **Method**: `PUT`
* **Headers**: `Content-Type: application/json`
* **Request Body Schema**:
  ```json
  {
    "remarks": "Verified certificates. Approved."
  }
  ```
* **Response (Success - 200 OK)**:
  ```json
  {
    "success": true
  }
  ```
* **Response (Invalid State - 400 Bad Request)**:
  ```json
  {
    "error": "Can only approve applications in 'Submitted' status."
  }
  ```

---

### 5. Reject Application (Admin Only)
Reject a submitted application. Transitions status to `Rejected`. Can only transition from `Submitted`.

* **URL**: `/students/<id>/reject`
* **Method**: `PUT`
* **Headers**: `Content-Type: application/json`
* **Request Body Schema**:
  ```json
  {
    "remarks": "Underage or invalid details provided."
  }
  ```
* **Response (Success - 200 OK)**:
  ```json
  {
    "success": true
  }
  ```

---

### 6. Track Registration Status (Public)
Public lookup utility to fetch registration status by email, phone, or registration ID.

* **URL**: `/students/track`
* **Method**: `GET`
* **Query Parameters**:
  * `query`: String (Required). Represents registration ID, email, or phone.
* **Response (Success - 200 OK)**:
  ```json
  {
    "registration_id": "REG1001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "01712345678",
    "course_name": "Computer Science",
    "status": "Submitted",
    "created_at": "2026-06-23 10:00:00"
  }
  ```
* **Response (Not Found - 404 Not Found)**:
  ```json
  {
    "error": "No matching registration record found."
  }
  ```

---

### 7. Export Registrations to CSV (Admin Only)
Download CSV file of matching registrations.

* **URL**: `/students/export`
* **Method**: `GET`
* **Query Parameters**: Same search/status filters as standard list GET `/students`.
* **Response (Success - 200 OK)**: Returns file stream data (`attachment; filename=student_registrations.csv`).
