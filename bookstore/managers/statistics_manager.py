"""
StatisticsManager [Class]

Responsibilities:
  - Compute total sales revenue for a given time period
  - Compute number of orders placed over a given time period
  - Identify best-selling books over a given time period
  - Return a formatted statistics report to the Store Manager
  - Validate the requested time period before processing a report

Collaborators: OrderManager, Order, Book

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
from datetime import datetime, timedelta

from managers import file_storage as storage
from models.order import Order

ORDERS_FILE = "orders.json"


class StatisticsManager:
    """Generates read-only sales and inventory reports from completed order data."""

    def __init__(self, catalogue_manager=None):
        self.catalogue_manager = catalogue_manager

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_orders(self):
        """Load all orders from storage."""
        raw = storage.load(ORDERS_FILE)
        return [Order.from_dict(d) for d in raw]

    @staticmethod
    def _parse_date(order):
        """Parse the created_at field of an order into a datetime object."""
        try:
            return datetime.strptime(order.created_at, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return None

    def _filter_by_period(self, orders, period):
        """
        Filter orders by time period.
        period: 'today', 'week', 'month', 'year', 'all'
        Returns filtered list of orders.
        """
        now = datetime.now()
        cutoffs = {
            "today": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "week":  now - timedelta(days=7),
            "month": now - timedelta(days=30),
            "year":  now - timedelta(days=365),
            "all":   None,
        }
        cutoff = cutoffs.get(period)
        if cutoff is None:
            return orders
        result = []
        for o in orders:
            dt = self._parse_date(o)
            if dt and dt >= cutoff:
                result.append(o)
        return result

    # ── Public interface ─────────────────────────────────────────────────────

    def get_summary(self, period="all"):
        """
        Return a summary dict for the given period:
          - total_revenue: float
          - order_count: int
          - avg_order_value: float
          - best_sellers: list of (title, quantity_sold) tuples, top 5
          - period_label: human-readable period string
        """
        orders = self._load_orders()
        filtered = self._filter_by_period(orders, period)

        period_labels = {
            "today": "Today",
            "week":  "Last 7 Days",
            "month": "Last 30 Days",
            "year":  "Last 365 Days",
            "all":   "All Time",
        }

        total_revenue = round(sum(o.total for o in filtered), 2)
        order_count   = len(filtered)
        avg_order     = round(total_revenue / order_count, 2) if order_count else 0.0

        # Tally book sales across all filtered orders
        book_sales = {}
        for order in filtered:
            for item in order.items:
                title = item.title
                book_sales[title] = book_sales.get(title, 0) + item.quantity

        best_sellers = sorted(book_sales.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "period_label":    period_labels.get(period, "All Time"),
            "total_revenue":   total_revenue,
            "order_count":     order_count,
            "avg_order_value": avg_order,
            "best_sellers":    best_sellers,
        }

    def get_recent_orders(self, period="all", limit=50):
        """Return the most recent orders for the given period, newest first."""
        orders = self._load_orders()
        filtered = self._filter_by_period(orders, period)
        filtered.sort(key=lambda o: self._parse_date(o) or datetime.min, reverse=True)
        return filtered[:limit]

    def get_status_breakdown(self, period="all"):
        """Return a dict of {status: count} for filtered orders."""
        orders = self._load_orders()
        filtered = self._filter_by_period(orders, period)
        breakdown = {}
        for o in filtered:
            breakdown[o.status] = breakdown.get(o.status, 0) + 1
        return breakdown
