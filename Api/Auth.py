# Auth.py

import sqlite3
from firebase_admin import db
from eth_account import Account
from eth_account.messages import encode_defunct
from checkInternet import check_internet_connection
from listUsers import list_users
from initdb import initialize_db


# Connection to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

def get_public_key_from_firebase(username):
    """Assigns a reference to the users' location in your Firebase database and queries for a user by their username."""
    ref = db.reference('users')
    snapshot = ref.order_by_child('username').equal_to(username).get()
    
    for key, val in snapshot.items():
        return val['public_key']
    
    return None  # If the user or public key is not found

def authenticate_user(number):
    """Combines user selection with authentication, including an internet connection check."""
    if not check_internet_connection(timeout=10):
        print("Authentication process aborted due to no Internet connection.")
        return
    
    try:
        initialize_db()
        list_users()
        if not number:
            user_selection = int(input("Enter the ID of the user you want to authenticate: "))
            print("User selection:", user_selection)
        else:
            user_selection = number
        
        # Connect to the SQLite database and select the user
        conn = sqlite3.connect('users.db')  # Ensure to change 'users.db' to your database name
        c = conn.cursor()
        c.execute("SELECT username, private_key FROM users WHERE id = ?", (user_selection,))
        user = c.fetchone()
        
        if user:
            username, private_key = user
            print(f"Attempting to authenticate {username}...")
            public_key = get_public_key_from_firebase(username)
            if public_key:
                public_key = public_key[2:] if public_key.startswith('0x') else public_key
                message = "Authentication Message"
                eth_encoded_message = encode_defunct(text=message)
                signed_message = Account.sign_message(eth_encoded_message, private_key=private_key)
                recovered_address = Account.recover_message(eth_encoded_message, signature=signed_message.signature)
                recovered_address = recovered_address[2:] if recovered_address.startswith('0x') else recovered_address
                if recovered_address.lower() == public_key.lower():
                    print(f"Authentication successful for {username}!")
                    return username
                else:
                    print("Authentication failed: Signature does not match the public key.")
            else:
                print(f"Public key for {username} not found in Firebase.")
        else:
            print("User not found.")
    except ValueError:
        print("Invalid input: Please enter a valid number.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        conn.close()  # Ensure to close the database connection
