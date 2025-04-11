# Kinetiq HR Management System Backend

A Django-based backend system for managing human resources including employee records, performance tracking, attendance, and departmental roles.

---

## Featured Submodules

### Human Resources Management
- **Department**: Complete
- **Department Superiors**: Complete
- **Positions**: Complete
- **Employees**: Complete
- **Employee Performance**: Complete
- **Employee Salary**: Complete

### Workforce Management
- **Attendance Tracking**: ~70% Done
- **Workforce Allocations**: ~80% Done

### Leave & Job Management
- **Leave Request**: Not Started
- **Leave Balances**: Not Started
- **Job Posting**: Not Started
- **Recruitment (Candidates, Interviews)**: Not Started

### Payroll & Calendar Management
- **Payroll**: Not Started
- **Calendar Dates**: ~50% Done

### Employee Lifecycle
- **Resignation**: Not Started

---

## Clone the Repository

```bash
git clone https://github.com/Kinetiq-PLM/kinetiq-erp-hr-management-backend.git
cd kinetiq-erp-hr-management-backend
```

---

## Setup Virtual Environment

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

---

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Configure Database

Open `hrm_backend/settings.py` and locate the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Kinetiq-DB-Schema',
        'USER': '<your_username>',
        'PASSWORD': '<your_password>',
        'HOST': 'localhost',
        'PORT': '<your_psql_port>',
        'OPTIONS': {
            'options': '-c search_path=human_resources'
        },
    }
}
```

---

## Database Setup

Make sure PostgreSQL is installed and running.

### Create & Import from SQL Dump

If you're using the provided `.sql` file:

```bash
psql -U <your_username> -c "CREATE DATABASE kinetiq_db;"
psql -U <your_username> kinetiq_db < db/kinetiq-hrm.sql
```

---

## Run the Server

```bash
python manage.py runserver
```

The server will be available at:  
http://127.0.0.1:8000/
