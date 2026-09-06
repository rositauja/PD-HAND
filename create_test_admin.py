# create_test_admin.py - Script to create an admin account

import sys
import os
import getpass

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.database import get_connection, hash_password, create_tables

# Create tables first
create_tables()

print("Create Admin Account")
print("--------------------")

name = input("Enter admin name: ").strip()
email = input("Enter admin email: ").strip()
password = getpass.getpass("Enter admin password: ")
confirm_password = getpass.getpass("Confirm admin password: ")

if password != confirm_password:
    print("❌ Passwords do not match.")
    sys.exit()

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO admin_auth (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        hash_password(password),
        "admin"
    ))

    conn.commit()
    print("✅ Admin account created successfully!")
    print(f"📧 Email: {email}")
    print("🔐 Password: set successfully")

except Exception as e:
    print(f"❌ Error: {e}")

    if "UNIQUE constraint failed" in str(e):
        print("An admin account already exists with this email.")

finally:
    conn.close()