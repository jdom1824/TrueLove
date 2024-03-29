# newUser.py

import sqlite3
from firebase_admin import db
from eth_account import Account
from listUsers import list_users

# Connection to SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()

def generate_keys():
    # Genera un nuevo par de claves usando Web3
    acct = Account.create()
    private_key = acct.key.hex()  # Ajuste para acceder a la clave privada
    public_key = acct.address
    return public_key, private_key


def register_user():
    while True:  # Starts a loop that will repeat the request until the condition is met.
        # Requests the username from the user.
        username = input('Enter your username to register: ')
        
        # Checks if the username is at least 4 characters long.
        if len(username) < 4:
            print("Username must be at least 4 characters long. Please try again.")
            continue  # Proceeds with the next iteration of the loop, asking for the username again.

        # Breaks the loop if the username is valid.
        break
    # key gen.
    public_key, private_key = generate_keys()

    # Reference to Firebase database.
    ref = db.reference('users')

    # Check if the username or public key is already registered in Firebase.
    if ref.order_by_child('username').equal_to(username).get():
        print("The username is already registered in Database.")
        return False
    if ref.order_by_child('public_key').equal_to(public_key).get():
        print("The public key is already registered in Database.")
        return False

    # Insert user into SQLite database.
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, public_key, private_key) VALUES (?, ?, ?)", 
                           (username, public_key, private_key))
            conn.commit()
            print("User registered successfully in SQLite.")
        except sqlite3.IntegrityError as e:
            print(f"SQLite Error: {e}")
            return False

    # Register the user in Firebase database.
    ref.push({
        'username': username,
        'public_key': public_key
    })
    print("User registered successfully in Firebase.")
    list_users()
    return True
