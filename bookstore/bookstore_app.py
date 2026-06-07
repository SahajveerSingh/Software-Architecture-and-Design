"""
BookstoreApp [Class]

Responsibilities:
  - Initialise and start up the online bookstore system
  - Create and wire up all manager class instances in the correct boot order
  - Provide a single access point to all subsystem managers
  - Handle top-level system shutdown and cleanup

Bootstrap order:
  Step 1: CatalogueManager   — books/stock must exist before any other subsystem
  Step 2: UserManager        — accounts must exist before authenticated actions
  Step 3: OrderManager       — depends on CatalogueManager + UserManager
  Step 4: PaymentProcessor   — relevant only once OrderManager exists
  Step 5: ShipmentManager    — shipments arise from paid orders
  Step 6: NotificationService — registers as observer on OrderManager + ShipmentManager
  Step 7: ReturnManager      — depends on OrderManager, PaymentProcessor, CatalogueManager
  Step 8: StatisticsManager  — derives data from OrderManager

Collaborators: UserManager, CatalogueManager, OrderManager,
               PaymentProcessor, ShipmentManager, NotificationService,
               ReturnManager, StatisticsManager

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from managers.user_manager import UserManager
from managers.statistics_manager import StatisticsManager


class BookstoreApp:
    """
    Top-level application controller and bootstrap entry point.
    Creates all manager instances in the correct dependency order.
    """

    def __init__(self):
        # Step 1: CatalogueManager (provided by Member 1)
        self.catalogue_manager = None   # registered via register_catalogue_manager()

        # Step 2: UserManager
        self.user_manager = UserManager()
        self.user_manager.seed_store_manager()

        # Step 3: OrderManager (provided by Member 3)
        self.order_manager = None       # registered via register_order_manager()

        # Steps 4–8: Further managers (placeholders)
        self.payment_processor = None
        self.shipment_manager = None
        self.notification_service = None
        self.return_manager = None
        self.statistics_manager = None

    # ── Registration hooks for other members ────────────────────────────────

    def register_catalogue_manager(self, catalogue_manager):
        """Register CatalogueManager once Member 1 provides it (Step 1)."""
        self.catalogue_manager = catalogue_manager

    def register_order_manager(self, order_manager):
        """Register OrderManager once Member 3 provides it (Step 3)."""
        self.order_manager = order_manager

    def register_payment_processor(self, payment_processor):
        """Register PaymentProcessor once available (Step 4)."""
        self.payment_processor = payment_processor

    def register_shipment_manager(self, shipment_manager):
        """Register ShipmentManager once available (Step 5)."""
        self.shipment_manager = shipment_manager

    def register_notification_service(self, notification_service):
        """
        Register NotificationService once available (Step 6).
        NotificationService must register itself as an observer on
        OrderManager and ShipmentManager after this call.
        """
        self.notification_service = notification_service

    def register_return_manager(self, return_manager):
        """Register ReturnManager once available (Step 7)."""
        self.return_manager = return_manager

    def register_statistics_manager(self, statistics_manager):
        """Register StatisticsManager once available (Step 8)."""
        self.statistics_manager = statistics_manager

    # ── System status ────────────────────────────────────────────────────────

    def is_ready(self):
        """
        Return True when all core managers are wired up.
        Core = UserManager + CatalogueManager + OrderManager.
        """
        return (
            self.user_manager is not None
            and self.catalogue_manager is not None
            and self.order_manager is not None
        )

    def shutdown(self):
        """Handle top-level system shutdown and cleanup."""
        if self.user_manager.is_logged_in():
            self.user_manager.logout()
