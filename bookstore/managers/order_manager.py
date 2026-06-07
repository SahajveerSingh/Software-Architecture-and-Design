"""
OrderManager [Class]

Responsibilities:
  - Manage volatile runtime session shopping carts using CartItem data-holders
  - Coordinate order processing pipelines, inventory adjustments, and billing entries
  - Persist transactions via the shared team flat-file JSON storage utility
  - Support distinct multi-role access routes (Customer History vs Manager Ledger Tracking)

"""

import os
from datetime import datetime

# Centralized team structural model and storage utility imports
from models.order import CartItem, OrderItem, Invoice, Order
from managers import file_storage as storage

ORDERS_FILE = "orders.json"

class OrderManager:
    """
    Handles memory-based customer shopping carts, checkout data persistence, 
    invoice production pipelines, and multi-user order tracking workflows.
    """
    def __init__(self, user_manager, catalogue_manager):
        self.user_manager = user_manager
        self.catalogue_manager = catalogue_manager
        self.active_carts = {}
        self.STATUS_FLOW = Order.STATUSES
        self.was_cleared = False

    def _load_orders(self):
        """Loads and reconstructs Order instances using the team's shared file storage engine."""
        raw = storage.load(ORDERS_FILE)
        return [Order.from_dict(d) for d in raw]

    def _save_orders(self, orders_list):
        """Serializes and logs order history datasets using the team's shared file storage engine."""
        storage.save(ORDERS_FILE, [o.to_dict() for o in orders_list])

    # ── Shopping Cart Logic (Volatile Memory Workspace) ────────────────────

    def get_cart(self, user_id):
        """Returns the specific customer item dictionary matching their active session."""
        if user_id not in self.active_carts:
            self.active_carts[user_id] = {}
        return self.active_carts[user_id]

    def add_to_cart(self, user_id, book_id, quantity=1):
        """Validates catalog stock thresholds prior to allocating units into a session cart."""
        book = self._find_book_by_id(book_id)
        if not book:
            return False, "Book item could not be located inside the active system catalogue."
            
        stock_available = getattr(book, "stock_quantity", 0)
        book_title = getattr(book, "title", "Unknown Book")
        book_price = getattr(book, "price", 0.0)
            
        current_cart = self.get_cart(user_id)
        existing_item = current_cart.get(book_id)
        existing_qty = existing_item.quantity if existing_item else 0
        target_qty = existing_qty + quantity
        
        if target_qty > stock_available:
            return False, f"Insufficient stock allocation. Available remaining items: {stock_available}."
            
        if target_qty <= 0:
            return self.remove_from_cart(user_id, book_id)
            
        current_cart[book_id] = CartItem(
            book_id=book_id,
            title=book_title,
            price=float(book_price),
            quantity=target_qty
        )
        return True, "Cart selection units successfully provisioned and updated."

    def remove_from_cart(self, user_id, book_id):
        """Purges an entire designated book row directly from the session cart workspace."""
        self.was_cleared = True
        if user_id in self.active_carts and book_id in self.active_carts[user_id]:
            del self.active_carts[user_id][book_id]
            return True, "Selected book profile completely removed from current cart."
        return False, "Item identifier targets not located inside the current cart context."

    def clear_cart(self, user_id):
        """Completely clears the specified user's active memory workspace cart."""
        self.was_cleared = True
        self.active_carts[user_id] = {}

    # ── Transactional Checkout Engine ──────────────────────────────────────────

    def checkout(self, user_id, delivery_address):
        """Transforms volatile cart items into historical database records and prints invoices."""
        if not delivery_address or not delivery_address.strip():
            return False, "Validation Failure: Physical delivery target parameters cannot be blank."
            
        cart = self.get_cart(user_id)
        if not cart:
            return False, "Operation Blocked: Current shopping cart is empty."
            
        order_items = []
        items_subtotal = 0.0
        
        for book_id, cart_item in list(cart.items()):
            book = self._find_book_by_id(book_id)
            stock = getattr(book, "stock_quantity", 0) if book else 0
            
            if cart_item.quantity > stock:
                return False, f"Stock changed mid-session. '{cart_item.title}' has only {stock} left."
                
            order_items.append(OrderItem(
                book_id=cart_item.book_id,
                title=cart_item.title,
                price_at_purchase=cart_item.price,
                quantity=cart_item.quantity
            ))
            items_subtotal += cart_item.line_total()

        for item in order_items:
            self._decrement_catalogue_stock(item.book_id, item.quantity)
            
        # Neutral fallback customer profile name assigned here to replace personal details
        customer_name = "Valued Customer"
        if hasattr(self.user_manager, "_load_users"):
            try:
                users_list = self.user_manager._load_users()
                current_user_obj = next((u for u in users_list if u.user_id == user_id), None)
                if current_user_obj:
                    customer_name = current_user_obj.name
            except Exception:
                pass
        
        gst_amount = round(items_subtotal * 0.10, 2)
        grand_total = round(items_subtotal + gst_amount, 2)
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        unique_timestamp = int(datetime.now().timestamp())
        order_id = f"ORD-{unique_timestamp}"
        invoice_id = f"INV-{unique_timestamp}"
        
        invoice_obj = Invoice(
            invoice_id=invoice_id, order_id=order_id, customer_name=customer_name,
            items_subtotal=items_subtotal, gst=gst_amount, total=grand_total, created_at=timestamp_str
        )
        
        new_order = Order(
            order_id=order_id, customer_id=user_id, customer_name=customer_name,
            items=order_items, total=grand_total, delivery_address=delivery_address.strip(),
            status="Placed", created_at=timestamp_str, invoice_id=invoice_id
        )
        
        all_orders = self._load_orders()
        all_orders.append(new_order)
        self._save_orders(all_orders)
        
        print(self.generate_invoice_string(invoice_obj, order_items))
        print("\n[SYSTEM NOTIFICATION]: Payment processed successfully.")
        
        self.clear_cart(user_id)
        return True, order_id

    # ── History Ledger & Multi-User Progress Workflows ───────────────────────

    def get_customer_order_history(self, user_id):
        all_orders = self._load_orders()
        return [o for o in all_orders if o.customer_id == user_id]

    def get_all_orders_for_manager(self):
        return self._load_orders()

    def update_order_status(self, order_id, new_status):
        if new_status not in self.STATUS_FLOW:
            return False, f"Invalid state input assignment. Choose from: {self.STATUS_FLOW}"
            
        orders = self._load_orders()
        for order in orders:
            current_id = order.order_id
            target_lookup = str(order_id).strip().replace("('", "").replace("',)", "")
            target_lookup = target_lookup.replace("('", "").replace("',", "").replace(")", "").strip()
            
            if current_id == target_lookup or target_lookup in current_id:
                order.status = new_status
                self._save_orders(orders)
                return True, f"Order tracking reference {current_id} successfully upgraded to '{new_status}'."
                
        return False, "Target tracking identifier missing from active registry context lines."

    def generate_invoice_string(self, invoice, items):
        divider = "=" * 50
        lines = [
            divider, "             FAVOURITE BOOKS INVOICE             ", divider,
            f"Invoice No: {invoice.invoice_id}", f"Order Ref:  {invoice.order_id}",
            f"Customer:   {invoice.customer_name}", f"Date/Time:  {invoice.created_at}", divider,
            f"{'Item Description':<25} {'Qty':<5} {'Subtotal':<10}"
        ]
        for item in items:
            lines.append(f"{item.title[:23]:<25} {item.quantity:<5} ${item.line_total():<10.2f}")
        lines.append(divider)
        lines.append(f"Items Subtotal:                    ${invoice.items_subtotal:.2f}")
        lines.append(f"GST (10%):                         ${invoice.gst:.2f}")
        lines.append(f"TOTAL AMOUNT PAID (AUD):           ${invoice.total:.2f}")
        lines.append(divider)
        return "\n".join(lines)

    def _find_book_by_id(self, book_id):
        if hasattr(self.catalogue_manager, "get_all_books"):
            all_books = self.catalogue_manager.get_all_books()
            return next((b for b in all_books if b.book_id == book_id or getattr(b, "isbn", "") == book_id), None)
        return None

    def _decrement_catalogue_stock(self, book_id, qty_to_deduct):
        book = self._find_book_by_id(book_id)
        if book and hasattr(self.catalogue_manager, "update_book"):
            new_stock = max(0, book.stock_quantity - qty_to_deduct)
            self.catalogue_manager.update_book(book_id=book.book_id, stock_quantity=new_stock)
