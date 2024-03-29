import sqlite3
from firebase_config import get_firebase_db_reference
from Auth import authenticate_user
import random
import time
import threading

def find_user_id_by_username(username):
    """Finds the user ID by username in Firebase."""
    ref = get_firebase_db_reference('users')
    users = ref.get()
    if users:  # Check if users is not None or empty
        for user_id, user_info in users.items():
            if user_info.get('username') == username:
                return user_id
    return None

def list_last_10_iterations_and_send_to_firebase(username):
    # Initialize Firebase
    #initialize_firebase()
    
    # Find the user ID for the given username
    user_id = find_user_id_by_username(username)
    if not user_id:
        print(f"Username {username} not found in Firebase.")
        return
    
    # Connect to the SQLite database
    conn = sqlite3.connect('last_10_iterations.db')
    c = conn.cursor()
    
    # Select the last 10 iterations
    c.execute('''SELECT iteration_number, private_key, address, time, wallets_per_second
                 FROM iterations
                 ORDER BY iteration_number DESC
                 LIMIT 10''')
    
    # Retrieve all results
    iterations = c.fetchall()
    
    if iterations:
        # Clear the iterations node for this user in Firebase
        iterations_path = f'users/{user_id}/iterations'
        ref = get_firebase_db_reference(iterations_path)
        ref.set({})  # This will clear all existing iterations

        proof_path = f'users/{user_id}/proof_of_love'
        proof_ref = get_firebase_db_reference(proof_path)
        proof_exists = proof_ref.get()

        if not proof_exists:
            # Executes only if it's the first time (proof_of_love doesn't exist)
            first_iteration = iterations[-1]  # The first iteration based on the current sorting
            proof_data = {
                'iteration_number': first_iteration[0],
                'private_key': first_iteration[1],
                'address': first_iteration[2],
                'time': first_iteration[3],
                'wallets_per_second': first_iteration[4]
            }
            proof_ref.set(proof_data)
            #print("Proof of Love iteration set for the first time.")
        
        # Reverse the iterations to send them in ascending order
        for iteration in reversed(iterations):
            iteration_number, private_key, address, time_elapsed, wallets_per_second = iteration
            
            data = {
                'iteration_number': iteration_number,
                'private_key': private_key,
                'address': address,
                'time': time_elapsed,
                'wallets_per_second': wallets_per_second
            }
            
            # Insert each new iteration
            new_ref = get_firebase_db_reference(f'{iterations_path}/{iteration_number}')
            new_ref.set(data)
            
    else:
        print("No iterations found for the specified range in the database.")
    
    # Close the database connection
    conn.close()

def run_in_background(username):
    while True:
        list_last_10_iterations_and_send_to_firebase(username)
        sleep_time = random.randint(120, 500)  # Random interval between 10 and 60 seconds
        #print(f"Waiting {sleep_time} seconds before the next execution...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    # Specify the username you are looking for
    user = authenticate_user(1)
    thread = threading.Thread(target=run_in_background, args=(user,))
    thread.daemon = True
    thread.start()
