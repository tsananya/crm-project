# crm-project
## Live demo
- Live: https://crm-project-55ln.onrender.com
- Mobile admin UI: https://crm-project-55ln.onrender.com/m/
- Free hosting: the first load can take about a minute, and data resets on restart (demo data is recreated automatically).
# Loan Sales & Call Centre CRM

A CRM for a loan intermediary company. The admin uploads and distributes leads to
call centre staff, tracks calls, documents and loan applications until disbursal.

## Tech stack
Python, Django 5, SQLite, Bootstrap 5, Chart.js, pandas/openpyxl

## Features
**Admin portal:** dashboard with stats and chart, employee management (add, edit,
deactivate, daily target), bulk lead upload (CSV/Excel), lead list with filters,
even lead distribution, document verification, bank and loan scheme management,
loan application tracking (applied → under review → approved → disbursed / rejected → closed),
reports with date and employee filters and CSV export.

**Staff portal:** assigned leads, daily call progress, call status and remarks,
follow-up scheduling and tracking, document upload, loan application creation,
personal performance chart.

**Mobile admin UI:** open `/m/` for the full admin portal in a mobile app-style
layout (top bar, bottom tabs). Use "Desktop view" in More to switch back.

## Access control
Users have a `role` (admin or staff). Every page is protected by a role decorator.
Staff can only open leads assigned to them; admin pages return 403 for staff.

## Run locally
```
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

## Test credentials
| Role | Username | Password |
|---|---|---|
| Admin | admin | Admin@123 |
| Staff | staff1 | Staff@123 |

## Notes
- Built within 24 hours. I was new to Django, so I used AI tools to learn and to
  generate boilerplate, and I reviewed, tested and debugged the code myself.
- Lead distribution is round-robin up to each employee's daily target.
- Not done / next steps: Postgres for production, cloud storage for uploaded
  documents, edit and delete for leads, automated tests.