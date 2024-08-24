import sys
import requests
import time
from getpass import getpass
import os
import threading

class AYETMS:
    def __init__(self):
        self.user_id = None
        self.total_time = 0
        self.is_break = False
        self.base_url = "https://ayetms-server.onrender.com/api"

    def login(self):
        self.user_id = input("User ID: ")
        password = getpass("Password: ")
        response = requests.post(f"{self.base_url}/login", json={"userId": self.user_id, "password": password})
        data = response.json()
        if data.get("success"):
            self.total_time = data.get("totalTime", 0)
            print("Login successful!")
            return True
        else:
            print("Login failed. Invalid user ID or password.")
            return False

    def fetch_employee_data(self):
        response = requests.get(f"{self.base_url}/employee?userId={self.user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"Name: {data['name']}")
            print(f"Designation: {data['designation']}")
            print(f"Role: {data['role']}")
            print(f"Billable Code: {data['billableCode']}")
        else:
            print("Failed to fetch employee data")

    def update_timer(self):
        if not self.is_break:
            self.total_time += 1
        print(f"\rWorking Hours: {self.format_time(self.total_time)}", end="", flush=True)

    def toggle_break(self):
        self.is_break = not self.is_break
        status = "Started" if self.is_break else "Ended"
        print(f"\nBreak {status}")
        requests.post(f"{self.base_url}/break", json={"userId": self.user_id, "isBreak": self.is_break})

    def logout(self):
        requests.post(f"{self.base_url}/logout", json={"userId": self.user_id, "timer": self.total_time})
        print("\nLogged out successfully")

    @staticmethod
    def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_input(prompt=""):
    if os.name == 'nt':  # For Windows
        import msvcrt
        print(prompt, end='', flush=True)
        return msvcrt.getch().decode('utf-8').lower()
    else:  # For Unix-like systems (Linux, macOS)
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()

def input_thread_function(ayetms):
    while True:
        key = get_input()
        if key == 'b':
            ayetms.toggle_break()
        elif key == 'q':
            break

def main():
    ayetms = AYETMS()
    if not ayetms.login():
        return

    ayetms.fetch_employee_data()
    print("\nCommands: 'b' for break (again press 'b' to back on work), 'q' to quit")
    
    input_thread = threading.Thread(target=input_thread_function, args=(ayetms,))
    input_thread.daemon = True
    input_thread.start()

    try:
        while input_thread.is_alive():
            ayetms.update_timer()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        ayetms.logout()

if __name__ == "__main__":
    main()