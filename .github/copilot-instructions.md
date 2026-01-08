# CuentasClaras - Flask Debt Management App

## Project Overview
Web application for managing personal loans and debts with user authentication and detailed tracking.

## Tech Stack
- Flask 3.0 + Flask-SQLAlchemy + Flask-Login
- Tailwind CSS for UI
- HTMX for dynamic updates
- SQLite database

## Database Models
- User: id, username, email, password_hash
- Debtor: id, user_id, name, phone, email, created_at
- Debt: id, debtor_id, amount, initial_date, has_installments, installments_total, installments_paid, paid, notes

## Features
- User authentication (register/login/logout)
- CRUD for debtors (people who owe money)
- CRUD for debts (each debtor can have multiple debts)
- Days counter (auto-calculated from initial_date)
- Installment tracking (optional)
- Mark debts as paid
- Total calculations per debtor and overall
- Responsive design

## Project Status
✅ Step 1: Project structure created
⏳ Step 2: Scaffold Flask app
⏳ Step 3: Create templates
⏳ Step 4: Install dependencies
⏳ Step 5: Documentation
