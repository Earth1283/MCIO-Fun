# A little breifing before we start
# This is a simple GUI application that fetches user data from the Mine-Craft.io API.
# However, it needs the requests library to be installed.
# So if you have not already, run pip install requests OR pip3 install requests
# This application allows users to enter a user ID and fetches their profile, likes, and friends data.
# The data is displayed in a formatted text box.
# The application uses the tkinter library for the GUI and the requests library for API calls.
# The application is designed to be user-friendly and provides error handling for various scenarios.
# Import necessary libraries
import tkinter as tk
from tkinter import messagebox
import requests
import json
from datetime import datetime
import threading

def convert_unix_timestamp(timestamp):
    """Converts a Unix timestamp to a human-readable date format."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def format_user_data(profile_data, likes_data, friends_data):
    """Formats the profile data, likes data, and friends data into a human-readable text format."""
    profile = profile_data.get("profile", {}).get("user", {})
    stats = profile_data.get("profile", {}).get("stats", {})
    
    # Get user profile details
    nickname = profile.get("nickname", "N/A")
    user_id = profile.get("id", "N/A")
    balance = profile.get("balance", 0)
    date_register = convert_unix_timestamp(profile.get("date_register", 0))
    last_login = convert_unix_timestamp(profile.get("last_login", 0))
    about = profile.get("about", "N/A")
    
    # Get user stats
    blocks_broken = stats.get("blocks_broken", 0)
    blocks_placed = stats.get("blocks_placed", 0)
    playtime = stats.get("playtime", 0)
    
    # Format likes data
    liked_users = likes_data.get("users", [])
    likes_count = len(liked_users)

    # Format friends data
    friends_ids = friends_data.get("friends", [])
    friends_count = len(friends_ids)
    friends_list = "\n".join([str(friend_id) for friend_id in friends_ids])

    formatted_data = (
        f"User ID: {user_id}\n"
        f"Nickname: {nickname}\n"
        f"Balance: {balance}\n"
        f"Date Registered: {date_register}\n"
        f"Last Login: {last_login}\n"
        f"About: {about}\n\n"
        f"Stats:\n"
        f"  Blocks Broken: {blocks_broken}\n"
        f"  Blocks Placed: {blocks_placed}\n"
        f"  Playtime (seconds): {playtime}\n\n"
        f"Likes Data:\n"
        f"  Number of Likes: {likes_count}\n\n"
        f"Friends Data:\n"
        f"  Total Friends: {friends_count}\n"
        f"  Friend IDs:\n{friends_list}\n"
    )
    
    return formatted_data

def fetch_data_in_thread():
    """Handles the data fetching in a separate thread."""
    user_id = user_id_entry.get()

    if not user_id:
        messagebox.showerror("Input Error", "Please enter a user ID.")
        return

    # Disable the fetch button while data is being fetched to prevent api spam and result malformation
    fetch_button.config(state=tk.DISABLED)

    # Call the fetch functions in the background thread
    thread = threading.Thread(target=fetch_user_data, args=(user_id,))
    thread.start()

def fetch_user_data(user_id):
    """Fetches profile, likes, and friends data."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }

    try:
        # Fetch profile data with disguised headers
        profile_url = f"https://mine-craft.io/api/profile/{user_id}"
        profile_response = requests.get(profile_url, headers=headers)
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        # Fetch likes data
        likes_url = f"https://mine-craft.io/api/likes/list?user_id={user_id}"
        likes_response = requests.get(likes_url, headers=headers)
        likes_response.raise_for_status()
        likes_data = likes_response.json()

        # Fetch friends data
        friends_url = f"https://mine-craft.io/api/friends/ids/list?user_id={user_id}"
        friends_response = requests.get(friends_url, headers=headers)
        friends_response.raise_for_status()
        friends_data = friends_response.json()

        # Format the data
        formatted_data = format_user_data(profile_data, likes_data, friends_data)

        # Update the GUI with the formatted data in the main thread
        json_output.delete(1.0, tk.END)  # Clear previous output
        json_output.insert(tk.END, formatted_data)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("API Error", f"An error occurred while fetching data: {e}")
    except ValueError:
        messagebox.showerror("Parsing Error", "Failed to parse the response from the API.")
    except Exception as e:
        messagebox.showerror("Unknown Error", f"An unknown error occurred: {e}")

    finally:
        # Re-enable the fetch button once the data has been fetched
        fetch_button.config(state=tk.NORMAL)

# Create the main window
root = tk.Tk()
root.title("MCIO User Lookup | API METHOD")

# User ID Label and Entry
user_id_label = tk.Label(root, text="Enter User ID below:")
user_id_label.pack(pady=10)
user_id_entry = tk.Entry(root, width=30)
user_id_entry.pack(pady=5)

# Fetch Data Button
fetch_button = tk.Button(root, text="Fetch User Data", command=fetch_data_in_thread)
fetch_button.pack(pady=10)

# JSON Output Text Box
json_output_label = tk.Label(root, text="User Info (retrieved from API):")
json_output_label.pack(pady=10)
json_output = tk.Text(root, height=20, width=80)
json_output.pack(pady=10)

# Start the GUI loop
root.mainloop()
