"""
Login Attempt Control System
----------------------------

Purpose:
    Prevent brute-force login attacks by:
    - Tracking failed login attempts
    - Applying progressive delays
    - Locking accounts for 15 minutes after 5 failures
    - Logging security events
    - Tracking attempts by username and IP address

Educational cybersecurity project.
"""

import time
import logging
from dataclasses import dataclass
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60

BASE_DELAY = 1
MAX_DELAY = 8


# ============================================================
# AUDIT LOGGING
# ============================================================

logging.basicConfig(
    filename="security_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ============================================================
# USER ACCOUNT
# ============================================================

@dataclass
class UserAccount:
    username: str
    password: str


# Demo accounts
USERS = {
    "admin": UserAccount(
        username="admin",
        password="Admin@123"
    ),

    "student": UserAccount(
        username="student",
        password="Student@123"
    )
}


# ============================================================
# LOGIN ATTEMPT TRACKER
# ============================================================

class LoginAttemptControl:

    def __init__(self):

        # Failed attempts by username
        self.failed_attempts = {}

        # Lockout expiration times
        self.locked_until = {}

        # Failed attempts by IP address
        self.ip_attempts = {}

    # --------------------------------------------------------
    # Check account lock
    # --------------------------------------------------------

    def is_locked(self, username):

        if username not in self.locked_until:
            return False

        current_time = time.time()
        unlock_time = self.locked_until[username]

        if current_time < unlock_time:
            remaining = int(unlock_time - current_time)

            print(
                f"[LOCKED] Account '{username}' is locked."
            )

            print(
                f"Try again in approximately "
                f"{remaining} seconds."
            )

            return True

        # Lockout expired
        del self.locked_until[username]
        self.failed_attempts[username] = 0

        logging.info(
            "LOCKOUT_EXPIRED | username=%s",
            username
        )

        return False

    # --------------------------------------------------------
    # Calculate progressive delay
    # --------------------------------------------------------

    def get_delay(self, username):

        attempts = self.failed_attempts.get(
            username,
            0
        )

        if attempts <= 0:
            return 0

        delay = BASE_DELAY ** attempts

        return min(delay, MAX_DELAY)

    # --------------------------------------------------------
    # Record failed login
    # --------------------------------------------------------

    def record_failure(self, username, ip):

        self.failed_attempts[username] = (
            self.failed_attempts.get(username, 0) + 1
        )

        self.ip_attempts[ip] = (
            self.ip_attempts.get(ip, 0) + 1
        )

        attempts = self.failed_attempts[username]

        logging.warning(
            "FAILED_LOGIN | username=%s | ip=%s | attempts=%d",
            username,
            ip,
            attempts
        )

        print(
            f"[FAILED] Invalid login."
        )

        print(
            f"Failed attempts: "
            f"{attempts}/{MAX_FAILED_ATTEMPTS}"
        )

        # Lock account after maximum failures
        if attempts >= MAX_FAILED_ATTEMPTS:

            self.locked_until[username] = (
                time.time() + LOCKOUT_SECONDS
            )

            logging.error(
                "ACCOUNT_LOCKED | username=%s | ip=%s | duration=900s",
                username,
                ip
            )

            print()
            print(
                f"[LOCKOUT] Account '{username}' "
                f"has been locked for 15 minutes."
            )

            return

        # Progressive delay
        delay = self.get_delay(username)

        if delay > 0:

            print(
                f"[RATE LIMIT] Waiting {delay} second(s)..."
            )

            time.sleep(delay)

    # --------------------------------------------------------
    # Successful login
    # --------------------------------------------------------

    def record_success(self, username, ip):

        self.failed_attempts[username] = 0

        logging.info(
            "SUCCESSFUL_LOGIN | username=%s | ip=%s",
            username,
            ip
        )

        print(
            f"[SUCCESS] Login successful."
        )

    # --------------------------------------------------------
    # Login function
    # --------------------------------------------------------

    def login(self, username, password, ip):

        print()
        print("=" * 60)
        print("LOGIN ATTEMPT")
        print("=" * 60)

        print(f"Username : {username}")
        print(f"IP       : {ip}")

        # Check lockout
        if self.is_locked(username):
            return False

        # Check username
        if username not in USERS:

            self.record_failure(
                username,
                ip
            )

            return False

        user = USERS[username]

        # Check password
        if password != user.password:

            self.record_failure(
                username,
                ip
            )

            return False

        # Successful authentication
        self.record_success(
            username,
            ip
        )

        return True

    # --------------------------------------------------------
    # Display security status
    # --------------------------------------------------------

    def show_status(self):

        print()
        print("=" * 60)
        print("SECURITY STATUS")
        print("=" * 60)

        print("\nFailed Attempts:")

        if not self.failed_attempts:
            print("No failed attempts.")

        else:
            for username, attempts in self.failed_attempts.items():

                print(
                    f"  {username}: {attempts}"
                )

        print("\nLocked Accounts:")

        if not self.locked_until:
            print("No locked accounts.")

        else:

            for username, unlock_time in self.locked_until.items():

                remaining = max(
                    0,
                    int(unlock_time - time.time())
                )

                print(
                    f"  {username}: "
                    f"{remaining} seconds remaining"
                )

        print()


# ============================================================
# INTERACTIVE LOGIN
# ============================================================

def interactive_login(controller):

    print()
    print("=" * 60)
    print("LOGIN ATTEMPT CONTROL SYSTEM")
    print("=" * 60)

    username = input("Username: ")
    password = input("Password: ")
    ip = input("IP Address: ")

    controller.login(
        username,
        password,
        ip
    )


# ============================================================
# BRUTE FORCE SIMULATION
# ============================================================

def simulate_bruteforce(controller):

    print()
    print("=" * 60)
    print("BRUTE-FORCE ATTACK SIMULATION")
    print("=" * 60)

    username = "admin"
    attacker_ip = "192.168.1.100"

    passwords = [
        "wrong1",
        "wrong2",
        "wrong3",
        "wrong4",
        "wrong5",
        "wrong6"
    ]

    for attempt, password in enumerate(
        passwords,
        start=1
    ):

        print()
        print(
            f"Attack attempt #{attempt}"
        )

        result = controller.login(
            username,
            password,
            attacker_ip
        )

        if not result:

            if username in controller.locked_until:

                print()
                print(
                    "[TEST PASSED] Account lockout "
                    "has been enforced."
                )

                break

    print()
    print("Brute-force simulation completed.")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    controller = LoginAttemptControl()

    while True:

        print()
        print("=" * 60)
        print("LOGIN ATTEMPT CONTROL SYSTEM")
        print("=" * 60)

        print("1. Login")
        print("2. Simulate Brute-Force Attack")
        print("3. Show Security Status")
        print("4. Exit")

        choice = input(
            "\nSelect an option: "
        )

        if choice == "1":

            interactive_login(
                controller
            )

        elif choice == "2":

            simulate_bruteforce(
                controller
            )

        elif choice == "3":

            controller.show_status()

        elif choice == "4":

            print(
                "\nExiting Login Attempt Control System."
            )

            break

        else:

            print(
                "\nInvalid option."
            )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()