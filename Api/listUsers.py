# listUsers.py

import sqlite3
from firebase_config import initialize_firebase
# Connection to the SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
initialize_firebase()
# Function to list users
def list_users():
    """Displays available users and returns True if there are any, False otherwise."""
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    if users:
        print("List of users --> KEEP YOUR PRIVATE KEY IN A SAFE PLACE FOR FUTURE REWARDS <-- ")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Public Key: {user[2]}, Private Key: {user[3]}")
        return True
    else:
        print("No users.")
        return False


