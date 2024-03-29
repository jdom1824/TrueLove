# init.py

def main():
    """
    Initializes the database, creates a new user if no users exist, and performs authentication.
    """
    from initdb import initialize_db
    from listUsers import list_users
    from newUser import register_user
    from Auth import authenticate_user
    from TrueLove import run_true_love
    from last10 import run_in_background
    import threading

    try:
        # Initialize the database
        initialize_db()
        
        # Check if any users exist, if not, create a new user
        if not list_users():
            if not register_user():
                print("Failed to register a new user.")
                return
        
        # Try to authenticate the user and get the username if successful
        username = authenticate_user(None)  # Assuming authenticate_user does not need arguments
        if not username:  # If authenticate_user returns None or False
            print("Authentication error.")
            return
        
        # Start TrueLove.py in a separate thread
        thread = threading.Thread(target=run_in_background, args=(username,))
        thread.daemon = True
        thread.start()
        
        # Execute the main True Love process
        run_true_love()

        # Here you can add any other logic you want to run in the main thread

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
