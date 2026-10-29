"""Promote an existing registered account to administrator."""
import os
import getpass
import mysql.connector

email = input("Email of the account to make admin: ").strip().lower()
connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "internhub"),
)
cursor = connection.cursor()
cursor.execute("UPDATE users SET is_admin=1 WHERE email=%s", (email,))
connection.commit()
if cursor.rowcount:
    print("Admin access enabled. Log out and log in again.")
else:
    print("No account found. Register in InternHub first, then run this script.")
cursor.close()
connection.close()
