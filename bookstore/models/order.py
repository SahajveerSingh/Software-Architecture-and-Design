"""
Order-related Data-Holder Classes

Classes defined here:

CartItem
  - Store and provide access to the referenced Book and selected quantity
  - Transient: exists only until cart is converted to Order or abandoned

OrderItem
  - Store and provide access to the referenced Book, quantity, and price
    at time of purchase (preserves price even if book price changes later)

Invoice
  - Store billing details, unique invoice number, and financial breakdowns
    generated during checkout
  - Kept separate from Order to maintain high cohesion

Order
  - Store and provide access to order identity, customer reference, status
  - Store and provide access to the list of OrderItems in this order
  - Store and provide access to the delivery address captured at time of order
  - Store and provide access to payment reference and invoice references

Collaborators:
  CartItem  → Book
  OrderItem → Book
  Order     → OrderItem, Invoice

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""


class CartItem:
    """Temporary line item in a customer's active shopping cart."""

    def __init__(self, book_id, title, price, quantity):
        self.book_id = book_id
        self.title = title
        self.price = float(price)
        self.quantity = int(quantity)

    def line_total(self):
        return round(self.price * self.quantity, 2)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "price": self.price,
            "quantity": self.quantity,
        }

    @staticmethod
    def from_dict(data):
        return CartItem(
            book_id=data["book_id"],
            title=data["title"],
            price=data["price"],
            quantity=data["quantity"],
        )


class OrderItem:
    """
    Immutable line item in a completed order.
    Records price at time of purchase for financial accuracy.
    """

    def __init__(self, book_id, title, price_at_purchase, quantity):
        self.book_id = book_id
        self.title = title
        self.price_at_purchase = float(price_at_purchase)
        self.quantity = int(quantity)

    def line_total(self):
        return round(self.price_at_purchase * self.quantity, 2)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "price_at_purchase": self.price_at_purchase,
            "quantity": self.quantity,
        }

    @staticmethod
    def from_dict(data):
        return OrderItem(
            book_id=data["book_id"],
            title=data["title"],
            price_at_purchase=data["price_at_purchase"],
            quantity=data["quantity"],
        )


class Invoice:
    """
    Billing record generated at checkout.
    Kept separate from Order to maintain high cohesion.
    """

    def __init__(self, invoice_id, order_id, customer_name,
                 items_subtotal, gst, total, created_at):
        self.invoice_id = invoice_id
        self.order_id = order_id
        self.customer_name = customer_name
        self.items_subtotal = float(items_subtotal)
        self.gst = float(gst)
        self.total = float(total)
        self.created_at = created_at

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "items_subtotal": self.items_subtotal,
            "gst": self.gst,
            "total": self.total,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data):
        return Invoice(
            invoice_id=data["invoice_id"],
            order_id=data["order_id"],
            customer_name=data["customer_name"],
            items_subtotal=data["items_subtotal"],
            gst=data["gst"],
            total=data["total"],
            created_at=data["created_at"],
        )


class Order:
    """
    Immutable record of a completed purchase.
    Links customer, items, and payment into a single historical record.
    """

    STATUSES = ["Placed", "Paid", "Dispatched", "Delivered"]

    def __init__(self, order_id, customer_id, customer_name,
                 items, total, delivery_address,
                 status, created_at, invoice_id=None):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.items = items
        self.total = float(total)
        self.delivery_address = delivery_address
        self.status = status
        self.created_at = created_at
        self.invoice_id = invoice_id

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "items": [i.to_dict() for i in self.items],
            "total": self.total,
            "delivery_address": self.delivery_address,
            "status": self.status,
            "created_at": self.created_at,
            "invoice_id": self.invoice_id,
        }

    @staticmethod
    def from_dict(data):
        return Order(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            customer_name=data["customer_name"],
            items=[OrderItem.from_dict(i) for i in data["items"]],
            total=data["total"],
            delivery_address=data["delivery_address"],
            status=data["status"],
            created_at=data["created_at"],
            invoice_id=data.get("invoice_id"),
        )
