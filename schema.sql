-- Student Registration System Schema
-- Fits SQLite, and is compatible with MySQL/PostgreSQL

DROP TABLE IF EXISTS status_history;
DROP TABLE IF EXISTS students;

-- Table: students
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    address TEXT NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Approved', 'Rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: status_history
CREATE TABLE status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    old_status VARCHAR(20) NOT NULL,
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Trigger to automatically update updated_at timestamp on student updates in SQLite
CREATE TRIGGER IF NOT EXISTS update_student_timestamp
AFTER UPDATE ON students
BEGIN
    UPDATE students SET updated_at = CURRENT_TIMESTAMP WHERE id = new.id;
END;
