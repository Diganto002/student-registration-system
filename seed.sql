-- Seed data for testing Student Registration System

-- Insert students
INSERT INTO students (registration_id, first_name, last_name, email, phone, date_of_birth, gender, address, course_name, status, created_at, updated_at)
VALUES 
('REG1001', 'John', 'Doe', 'john.doe@example.com', '01712345678', '2005-05-15', 'Male', '123 Main St, Springfield', 'Computer Science', 'Submitted', '2026-06-23 10:00:00', '2026-06-23 10:00:00'),
('REG1002', 'Jane', 'Smith', 'jane.smith@example.com', '01887654321', '2004-08-22', 'Female', '456 Oak Rd, Metropolis', 'Mechanical Engineering', 'Approved', '2026-06-22 09:00:00', '2026-06-22 11:30:00');

-- Insert status history
INSERT INTO status_history (student_id, old_status, new_status, changed_by, changed_at, remarks)
VALUES
(1, 'None', 'Submitted', 'System', '2026-06-23 10:00:00', 'Initial registration submission.'),
(2, 'None', 'Submitted', 'System', '2026-06-22 09:00:00', 'Initial registration submission.'),
(2, 'Submitted', 'Approved', 'Admin', '2026-06-22 11:30:00', 'Credentials and documents verified.');
