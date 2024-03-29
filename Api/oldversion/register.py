import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase Configuration
cred = credentials.Certificate("/Users/jdom/TrueLove/TrueLove/Api/credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://truelove-78718-default-rtdb.firebaseio.com/'
})

# Connection to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Function to register users
def register_user(public_key):
    # Reference to Firebase database
    ref = db.reference('users')

    # Check if the public key is already registered
    if ref.order_by_child('public_key').equal_to(public_key).get():
        print("The public key is already registered.")
        return False

    # Register the user in the database
    ref.push({
        'public_key': public_key
    })
    print("User registered successfully.")
    return True

# Function to list available users
def list_users():
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    if users:
        print("Available users:")
        for i, user in enumerate(users, start=1):
            print(f"{i}. ID: {user[0]}, Username: {user[1]}")
    else:
        print("No users registered.")

# Function to select a user and register in Firebase
def select_and_register_user():
    # Show available users
    list_users()

    # Prompt user to select a user
    user_selection = input("Enter the number of the user you want to register in Firebase: ")

    # Validate user selection
    try:
        user_index = int(user_selection) - 1
        if user_index >= 0:
            # Get ID of selected user
            c.execute("SELECT public_key FROM users")
            users = c.fetchall()
            if users and user_index < len(users):
                public_key = users[user_index][0]
                # Register user in Firebase
                register_user(public_key)
            else:
                print("User number out of range.")
        else:
            print("Invalid user number.")
    except ValueError:
        print("Please enter a valid number.")

if __name__ == '__main__':
    # Select and register user in Firebase
    select_and_register_user()



