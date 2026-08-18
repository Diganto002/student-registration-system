# Student Registration System

A full-stack **Student Registration System** featuring Node.js, Express.js, SQLite, strict validation middleware (`express-validator`), status transition workflow engine, Admin authentication system, interactive OpenAPI (Swagger) API documentation, and a responsive Tailwind CSS portal.

**University:** University Of Liberal Arts Bangladesh (ULAB)

---

## 📂 Project Deliverables & Submission Package (`docs/` Folder)

All required submission documents, database DDL scripts, API specifications, Postman collection, and ER diagram are packaged in the **`docs/`** directory:

```text
docs/
 ├── database/
 │   └── schema.sql              1. SQLite DDL Schema Script
 ├── api_documentation.md        2. Full API Documentation Specification
 ├── postman_collection.json     3. Postman Collection (v2.1 Importable JSON)
 └── er_diagram.md               4. ER Diagram (Mermaid & ASCII Architecture)
```

---

## 🌟 Key Features

- **Self-Service Registration:** Students submit registration details with real-time field validation.
- **Default Application Status:** All new submissions start with `status = Submitted`.
- **System-Generated Unique ID:** Auto-generates sequential registration IDs (e.g. `REG1001`, `REG1002`).
- **Strict Input Validation Engine:**
  - `first_name` & `last_name`: Required, 2-50 characters, alphabets and spaces only.
  - `email`: Required, unique, valid email format.
  - `phone`: Required, unique, exact 11 digits (e.g., `01712345678`).
  - `date_of_birth`: Required, past date, **minimum age requirement is 16 years**.
  - `gender`: Required (`Male`, `Female`, `Other`).
  - `address`: Required, max 255 characters.
  - `course_name`: Required dropdown (`CSE`, `SE`, `DSAI`, `EEE`, `BBA`, `MSJ`).
- **🔐 Dedicated Admin Authentication:**
  - **Admin Username:** `spetrum`
  - **Admin Password:** `admin123`
- **Workflow State Machine:**
  - `Submitted` &rarr; `Approved` OR `Submitted` &rarr; `Rejected`.
  - **Rule:** Applications marked `Approved` or `Rejected` CANNOT be reverted to `Submitted` or re-processed.
- **Audit Log History:** Tracks all status changes with timestamps, old/new status, and admin remarks in a `status_history` table.
- **Auto-Generated Swagger OpenAPI UI:** Live interactive API documentation at `/api-docs` and raw spec at `/swagger.json`.

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
npm install
```

### 2. Run Application
```bash
npm start
```

- **Home Portal:** `http://localhost:3000`
- **Student Form:** `http://localhost:3000/register.html`
- **Admin Login:** `http://localhost:3000/admin-login.html`
- **Admin Dashboard:** `http://localhost:3000/dashboard.html`
- **Interactive Swagger API Docs:** `http://localhost:3000/api-docs`

---

## 🧪 Automated Test Suite
Run the verification test suite:
```bash
node scripts/verify_api.js
```

---

## 👤 Author & Credentials
- **University:** University Of Liberal Arts Bangladesh (ULAB)
- **Admin Credentials:** `spetrum` / `admin123`
- **Developer:** MHDiganto (mhdiganto@gmail.com)
- **GitHub:** https://github.com/Diganto002/student-registration-system
- **License:** ISC
