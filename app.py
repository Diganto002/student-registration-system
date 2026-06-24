from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, make_response
import os
import csv
import io
from datetime import datetime

from database import get_db, init_db, query_db, execute_db, close_db
from validation import validate_registration_data

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-registration-admin-key-123')

# Close DB connections at teardown
app.teardown_appcontext(close_db)

# Pre-configured Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Initialize database on startup
with app.app_context():
    init_db()

# Decorator to secure admin pages
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json:
                return jsonify({"error": "Unauthorized admin access."}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- PAGE ROUTES -----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student')
def student_portal():
    return render_template('student.html')

@app.route('/admin')
@admin_required
def admin_portal():
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('admin_portal'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = ADMIN_USERNAME
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_portal'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    if request.method == 'POST':
        return jsonify({"success": True})
    return redirect(url_for('login'))

# ----------------- API ENDPOINTS -----------------

# 1. Create a student registration
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json() or {}
    
    # Validation
    errors = validate_registration_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
        
    try:
        # Generate custom sequential registration ID (e.g. REG1001)
        # Select current max value of digits in registration_id
        # SUBSTR(registration_id, 4) parses 'REG1001' into '1001'
        db = get_db()
        cursor = db.execute("SELECT MAX(CAST(SUBSTR(registration_id, 4) AS INTEGER)) as max_val FROM students")
        row = cursor.fetchone()
        max_val = row['max_val'] if row and row['max_val'] else 1000
        new_reg_id = f"REG{max_val + 1}"
        
        # Insert student record
        cursor = db.execute(
            """INSERT INTO students (registration_id, first_name, last_name, email, phone, date_of_birth, gender, address, course_name, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted')""",
            (
                new_reg_id,
                data['first_name'].strip(),
                data['last_name'].strip(),
                data['email'].strip().lower(),
                data['phone'].strip(),
                data['date_of_birth'],
                data['gender'],
                data['address'].strip(),
                data['course_name']
            )
        )
        student_id = cursor.lastrowid
        
        # Write history trail
        db.execute(
            """INSERT INTO status_history (student_id, old_status, new_status, changed_by, remarks)
               VALUES (?, 'None', 'Submitted', 'System', 'Initial registration submission.')""",
            (student_id,)
        )
        db.commit()
        
        return jsonify({
            "success": True,
            "id": student_id,
            "registration_id": new_reg_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500

# 2. Get students matching filter conditions (Admin only)
@app.route('/students', methods=['GET'])
@admin_required
def get_students():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    
    # Query building with filters
    query_parts = []
    params = []
    
    if search:
        query_parts.append("(registration_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?)")
        # search string matching
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
        
    if status:
        query_parts.append("status = ?")
        params.append(status)
        
    where_clause = ""
    if query_parts:
        where_clause = "WHERE " + " AND ".join(query_parts)
        
    # Count total matching query
    count_query = f"SELECT COUNT(*) as count FROM students {where_clause}"
    count_row = query_db(count_query, params, one=True)
    total = count_row['count'] if count_row else 0
    
    # Get listing
    list_query = f"SELECT * FROM students {where_clause} ORDER BY id DESC LIMIT ? OFFSET ?"
    list_params = params + [limit, offset]
    students = query_db(list_query, list_params)
    
    student_list = []
    for s in students:
        student_list.append({
            "id": s['id'],
            "registration_id": s['registration_id'],
            "first_name": s['first_name'],
            "last_name": s['last_name'],
            "email": s['email'],
            "phone": s['phone'],
            "date_of_birth": s['date_of_birth'],
            "gender": s['gender'],
            "address": s['address'],
            "course_name": s['course_name'],
            "status": s['status'],
            "created_at": s['created_at']
        })
        
    return jsonify({
        "students": student_list,
        "total": total
    })

# 3. Get detailed student record + history logs (Admin only)
@app.route('/students/<int:id>', methods=['GET'])
@admin_required
def get_student_details(id):
    student = query_db("SELECT * FROM students WHERE id = ?", (id,), one=True)
    if not student:
        return jsonify({"error": "Student record not found."}), 404
        
    history = query_db("SELECT * FROM status_history WHERE student_id = ? ORDER BY changed_at DESC", (id,))
    
    student_data = {
        "id": student['id'],
        "registration_id": student['registration_id'],
        "first_name": student['first_name'],
        "last_name": student['last_name'],
        "email": student['email'],
        "phone": student['phone'],
        "date_of_birth": student['date_of_birth'],
        "gender": student['gender'],
        "address": student['address'],
        "course_name": student['course_name'],
        "status": student['status'],
        "created_at": student['created_at'],
        "updated_at": student['updated_at']
    }
    
    history_data = []
    for h in history:
        history_data.append({
            "id": h['id'],
            "old_status": h['old_status'],
            "new_status": h['new_status'],
            "changed_by": h['changed_by'],
            "changed_at": h['changed_at'],
            "remarks": h['remarks']
        })
        
    return jsonify({
        "student": student_data,
        "history": history_data
    })

# 4. Approve student (Admin only, only from Submitted status)
@app.route('/students/<int:id>/approve', methods=['PUT'])
@admin_required
def approve_student(id):
    db = get_db()
    student = query_db("SELECT * FROM students WHERE id = ?", (id,), one=True)
    if not student:
        return jsonify({"error": "Student record not found."}), 404
        
    if student['status'] != 'Submitted':
        return jsonify({"error": "Can only approve applications in 'Submitted' status."}), 400
        
    req_data = request.get_json() or {}
    remarks = req_data.get('remarks', '').strip() or 'Registration Approved by Administrator.'
    
    try:
        # Update student status
        db.execute("UPDATE students SET status = 'Approved' WHERE id = ?", (id,))
        # Log action history
        db.execute(
            """INSERT INTO status_history (student_id, old_status, new_status, changed_by, remarks)
               VALUES (?, 'Submitted', 'Approved', 'Admin', ?)""",
            (id, remarks)
        )
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": f"Failed to approve: {str(e)}"}), 500

# 5. Reject student (Admin only, only from Submitted status)
@app.route('/students/<int:id>/reject', methods=['PUT'])
@admin_required
def reject_student(id):
    db = get_db()
    student = query_db("SELECT * FROM students WHERE id = ?", (id,), one=True)
    if not student:
        return jsonify({"error": "Student record not found."}), 404
        
    if student['status'] != 'Submitted':
        return jsonify({"error": "Can only reject applications in 'Submitted' status."}), 400
        
    req_data = request.get_json() or {}
    remarks = req_data.get('remarks', '').strip() or 'Registration Rejected by Administrator.'
    
    try:
        # Update student status
        db.execute("UPDATE students SET status = 'Rejected' WHERE id = ?", (id,))
        # Log action history
        db.execute(
            """INSERT INTO status_history (student_id, old_status, new_status, changed_by, remarks)
               VALUES (?, 'Submitted', 'Rejected', 'Admin', ?)""",
            (id, remarks)
        )
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": f"Failed to reject: {str(e)}"}), 500

# 6. Lookup registration status by Email, Phone, or Registration ID (Public)
@app.route('/students/track', methods=['GET'])
def track_student():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Tracking query string is required."}), 400
        
    student = query_db(
        "SELECT * FROM students WHERE registration_id = ? OR email = ? OR phone = ?",
        (query, query.lower(), query),
        one=True
    )
    
    if not student:
        return jsonify({"error": "No matching registration record found."}), 404
        
    # Return limited public info to protect privacy (exclude date of birth & address if required, but let's send standard details for lookup)
    return jsonify({
        "registration_id": student['registration_id'],
        "first_name": student['first_name'],
        "last_name": student['last_name'],
        "email": student['email'],
        "phone": student['phone'],
        "course_name": student['course_name'],
        "status": student['status'],
        "created_at": student['created_at']
    })

# 7. CSV Export (Admin only)
@app.route('/students/export', methods=['GET'])
@admin_required
def export_students_csv():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    
    query_parts = []
    params = []
    
    if search:
        query_parts.append("(registration_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?)")
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])
        
    if status:
        query_parts.append("status = ?")
        params.append(status)
        
    where_clause = ""
    if query_parts:
        where_clause = "WHERE " + " AND ".join(query_parts)
        
    students = query_db(f"SELECT * FROM students {where_clause} ORDER BY id DESC", params)
    
    # Compile CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Registration ID', 'First Name', 'Last Name', 'Email', 'Phone', 
        'Date of Birth', 'Gender', 'Address', 'Course Name', 'Status', 'Registered At'
    ])
    
    for s in students:
        writer.writerow([
            s['registration_id'],
            s['first_name'],
            s['last_name'],
            s['email'],
            s['phone'],
            s['date_of_birth'],
            s['gender'],
            s['address'],
            s['course_name'],
            s['status'],
            s['created_at']
        ])
        
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=student_registrations.csv"
    response.headers["Content-type"] = "text/csv"
    return response

# Main run setup
if __name__ == '__main__':
    # Bind to localhost
    app.run(host='127.0.0.1', port=5000, debug=True)
