"""
Customer [Data-Holder Class]

Responsibilities:
  - Store and provide access to customer identity and contact details
  - Store and provide access to the user's role for access control decisions
  - Store delivery address used for order dispatch

Collaborators: None (pure data-holder — no behaviour)

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""


class Customer:
    """Data-holder for a registered user account."""

    def __init__(self, user_id, name, email, password_hash,
                 role, address="", failed_attempts=0,
                 locked=False, verified=False, last_active=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role                        # "Customer" or "StoreManager"
        self.address = address
        self.failed_attempts = failed_attempts
        self.locked = locked
        self.verified = verified
        self.last_active = last_active

    def to_dict(self):
        """Serialise to dict for JSON persistence."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "address": self.address,
            "failed_attempts": self.failed_attempts,
            "locked": self.locked,
            "verified": self.verified,
            "last_active": self.last_active,
        }

    @staticmethod
    def from_dict(data):
        """Deserialise from a dict loaded from JSON storage."""
        return Customer(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=data["role"],
            address=data.get("address", ""),
            failed_attempts=data.get("failed_attempts", 0),
            locked=data.get("locked", False),
            verified=data.get("verified", False),
            last_active=data.get("last_active"),
        )
