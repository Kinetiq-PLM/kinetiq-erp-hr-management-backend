# Kinetiq HR Management System Backend

A Django-based backend system for managing human resources including employee records, performance tracking, attendance, and departmental roles.

---

## Featured Submodules

### Human Resources Management
- **Department**: [Complete]
- **Department Superiors**: [Complete]
- **Positions**: [Complete]
- **Employees**: [Complete]
- **Employee Performance**: [Complete]
- **Employee Salary**: [Complete]

### Workforce Management
- **Attendance Tracking**: [Complete]
- **Workforce Allocations**: [Complete]

### Leave & Job Management
- **Leave Request**: [Complete]
- **Leave Balances**: [Complete]
- **Job Posting**: [Complete]
- **Recruitment (Candidates, Interviews)**: [Complete]

### Payroll & Calendar Management
- **Payroll**: [Complete]
- **Calendar Dates**: [Complete]

### Employee Lifecycle
- **Resignation**: [Complete]

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
source venv/bin/activate
pip install -r requirements.txt
```
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

Or if you are now connected to the RDS go to `hrm_backend/settings.py` and locate the `DATABASES` section and change it to:

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
