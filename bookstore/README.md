Favourite Books — Online Bookstore
SWE30003 Software Architectures and Design — Assignment 3
=========================================================

## HOW TO RUN

Requirements: Python 3.8 or higher (tkinter included with standard Python)

1. Open a terminal and navigate to this folder:
   cd bookstore

2. Run the application:
   python main.py

3. Default Store Manager login:
   Email: admin@favouritebooks.com
   Password: Admin@123

4. To create a Customer account, click "Create Account" on the login screen.

## FOLDER STRUCTURE

bookstore/
main.py Entry point — run this
bookstore_app.py Bootstrap controller
models/
customer.py Customer data-holder
book.py Book data-holder
order.py CartItem, OrderItem, Invoice, Order data-holders
**init**.py
managers/
file_storage.py Shared JSON persistence helper
user_manager.py Account & authentication logic (Member 2)
catalogue_manager.py [Member 1 — to be added]
order_manager.py [Member 3 — to be added]
**init**.py
ui/
auth_ui.py Login, Register, UpdateAccount, Profile windows
main_window.py Main navigation window (role-based sidebar)
catalogue_ui.py [to be added]
order_ui.py [to be added]
**init**.py
data/
users.json Persistent user accounts (auto-created on first run)
books.json Persistent book catalogue (auto-created by M1)
orders.json Persistent orders (auto-created by M3)
README.txt This file

## IMPLEMENTED BUSINESS AREAS

Area 1 — Account & Authentication: COMPLETE

- Register with full validation (email format, password strength, no duplicates)
- Login with SHA-256 password check and lockout after 5 failed attempts
- Logout clears session
- Update account (name, address, password — requires current password)
- View profile (read-only)
- Role-based navigation (Customer vs Store Manager)

Area 2 — Catalogue Management:
Area 3 — Shopping & Orders:  
Area 4 — Order Tracking:

## CODING STANDARD

This codebase follows PEP 8 — Style Guide for Python Code.
Van Rossum, G., Warsaw, B., & Coghlan, A. (2001). PEP 8 — Style Guide for
Python Code. Python Software Foundation. https://peps.python.org/pep-0008/
