"""
UserManager [Class]

Responsibilities:
  - Register a new customer account with validated credentials
  - Authenticate a user by verifying email and password
  - Determine the role of an authenticated user (Customer or Store Manager)
  - Create and maintain an active session for a logged-in user
  - Invalidate a session on logout or after inactivity timeout
  - Update a customer's account details (name, address, password)
  - Validate that an email address is not already registered
  - Enforce password strength rules during registration and password change

Collaborators: Customer

Design notes:
  - Centralises all authentication and security logic
  - Only authorised Store Managers access catalogue management operations
  - Passwords stored as SHA-256 hashes — plaintext never persisted
  - Account locked after 5 failed login attempts
  - Session stored as in-memory dict {user_id, role, name} — cleared on logout

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import hashlib
import re
import uuid
from datetime import datetime, timezone

from models.customer import Customer
from managers import file_storage as storage

USERS_FILE = "users.json"
MAX_LOGIN_ATTEMPTS = 5


class UserManager:
    """Manages all user accounts and authentication for the bookstore."""

    def __init__(self):
        self._session = None   # {user_id, role, name} or None when logged out

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _hash_password(password):
        """Return the SHA-256 hex digest of a plaintext password."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _now_iso():
        """Return the current UTC time as an ISO-8601 string."""
        return datetime.now(timezone.utc).isoformat()

    def _load_users(self):
        """Load all users from storage and return as a list of Customer objects."""
        raw = storage.load(USERS_FILE)
        return [Customer.from_dict(d) for d in raw]

    def _save_users(self, users):
        """Serialise a list of Customer objects and persist to storage."""
        storage.save(USERS_FILE, [u.to_dict() for u in users])

    @staticmethod
    def _find_by_email(email, users):
        """Return the Customer whose email matches (case-insensitive), or None."""
        email_lower = email.strip().lower()
        return next((u for u in users if u.email.lower() == email_lower), None)

    @staticmethod
    def _validate_password(password):
        """
        Enforce password strength rules.
        Returns (True, "") on success or (False, reason) on failure.
        Rules: 8+ chars, at least one uppercase, one digit, one special character.
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
            return False, "Password must contain at least one special character."
        return True, ""

    @staticmethod
    def _validate_email(email):
        """Return True if email matches a basic RFC-style format."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email.strip()))

    # ── Public interface ─────────────────────────────────────────────────────

    def register(self, name, email, password, address=""):
        """
        Register a new Customer account with validated credentials.

        Validates:
          - Name not empty
          - Email format and uniqueness
          - Password strength

        Returns: (success: bool, message: str)
        """
        name = name.strip()
        email = email.strip()

        if not name:
            return False, "Name cannot be empty."

        if not self._validate_email(email):
            return False, "Please enter a valid email address."

        ok, msg = self._validate_password(password)
        if not ok:
            return False, msg

        users = self._load_users()

        if self._find_by_email(email, users):
            return False, "An account with this email address already exists."

        new_customer = Customer(
            user_id=str(uuid.uuid4()),
            name=name,
            email=email.lower(),
            password_hash=self._hash_password(password),
            role="Customer",
            address=address.strip(),
            failed_attempts=0,
            locked=False,
            verified=True,
            last_active=self._now_iso(),
        )
        users.append(new_customer)
        self._save_users(users)
        return True, "Account created successfully. You can now log in."

    def login(self, email, password):
        """
        Authenticate a user by verifying email and password.
        Sets an in-memory session on success.
        Enforces account lockout after MAX_LOGIN_ATTEMPTS failures.

        Returns: (success: bool, message: str, role: str | None)
        """
        users = self._load_users()
        user = self._find_by_email(email, users)

        if user is None:
            return False, "No account found with that email address.", None

        if user.locked:
            return False, "This account has been locked after too many failed attempts. Please contact support.", None

        if user.password_hash != self._hash_password(password):
            user.failed_attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - user.failed_attempts
            if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                user.locked = True
                self._save_users(users)
                return False, "Account locked after too many failed attempts. Please contact support.", None
            self._save_users(users)
            return False, f"Incorrect password. {remaining} attempt(s) remaining.", None

        # Successful login — reset failure counter and open session
        user.failed_attempts = 0
        user.last_active = self._now_iso()
        self._save_users(users)

        self._session = {
            "user_id": user.user_id,
            "role": user.role,
            "name": user.name,
        }
        return True, f"Welcome back, {user.name}!", user.role

    def logout(self):
        """Invalidate the current session."""
        self._session = None

    def is_logged_in(self):
        """Return True if a session is currently active."""
        return self._session is not None

    def get_session(self):
        """Return the current session dict, or None."""
        return self._session

    def current_user_id(self):
        """Return the user_id from the active session, or None."""
        return self._session["user_id"] if self._session else None

    def current_role(self):
        """Return the role from the active session, or None."""
        return self._session["role"] if self._session else None

    def update_account(self, new_name=None, new_address=None,
                       current_password=None, new_password=None):
        """
        Update the logged-in customer's account details.
        Requires current password before allowing a password change.

        Returns: (success: bool, message: str)
        """
        if not self.is_logged_in():
            return False, "You must be logged in to update your account."

        users = self._load_users()
        user = next(
            (u for u in users if u.user_id == self.current_user_id()), None
        )
        if user is None:
            return False, "Account not found."

        if new_name is not None:
            new_name = new_name.strip()
            if not new_name:
                return False, "Name cannot be empty."
            user.name = new_name
            self._session["name"] = new_name

        if new_address is not None:
            user.address = new_address.strip()

        if new_password:
            if not current_password:
                return False, "Please enter your current password to set a new one."
            if user.password_hash != self._hash_password(current_password):
                return False, "Current password is incorrect."
            ok, msg = self._validate_password(new_password)
            if not ok:
                return False, msg
            user.password_hash = self._hash_password(new_password)

        user.last_active = self._now_iso()
        self._save_users(users)
        return True, "Your account details have been updated successfully."

    def get_user_profile(self):
        """Return a profile dict for the logged-in user, or None."""
        if not self.is_logged_in():
            return None
        users = self._load_users()
        user = next(
            (u for u in users if u.user_id == self.current_user_id()), None
        )
        if user is None:
            return None
        return {
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "role": user.role,
        }

    def seed_store_manager(self):
        """
        Create the default Store Manager account at bootstrap if none exists.
        Called by BookstoreApp during system initialisation.
        """
        users = self._load_users()
        if self._find_by_email("admin@favouritebooks.com", users):
            return
        manager = Customer(
            user_id=str(uuid.uuid4()),
            name="Store Manager",
            email="admin@favouritebooks.com",
            password_hash=self._hash_password("Admin@123"),
            role="StoreManager",
            address="Favourite Books, Glenferrie Rd, Hawthorn VIC 3122",
            failed_attempts=0,
            locked=False,
            verified=True,
            last_active=self._now_iso(),
        )
        users.append(manager)
        self._save_users(users)
