# checkInternet.py

import threading
from threading import Event
import requests
import time
import sys


def spinner(stop_event):
    """Displays a loading spinner in the console."""
    spinner_chars = ["|", "/", "-", "\\"]
    while not stop_event.is_set():
        for char in spinner_chars:
            sys.stdout.write('\r' + char)
            sys.stdout.flush()
            time.sleep(0.1)
            if stop_event.is_set():
                # Clean up the spinner line before exiting
                sys.stdout.write('\r' + ' ' * len(char) + '\r')
                sys.stdout.flush()
                return


def check_internet_connection(timeout=20):
    """Checks for an Internet connection with an extended timeout."""
    print("Verifying Internet connection...")
    stop_event = Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,), daemon=True)
    spinner_thread.start()

    url = "http://www.google.com"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises an error if the response is not successful
        # Ensure the spinner is cleared before printing the next message
        stop_event.set()
        spinner_thread.join()  # Wait for the spinner thread to finish
        print("\rInternet connection is stable.    ")
        return True
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as err:
        # Ensure the spinner is cleared before printing the error message
        stop_event.set()
        spinner_thread.join()  # Wait for the spinner thread to finish
        print(f"\rNo Internet connection: {err}    ")
        return False