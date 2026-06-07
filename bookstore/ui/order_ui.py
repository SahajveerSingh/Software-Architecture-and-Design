"""
OrderSystemWindow [Class]

Responsibilities:
  - Render an adaptive user interface panel mapping to active roles
  - Provide Customers with a quantitative 3-column Shopping Cart view layout
  - Provide Store Managers with an unconstrained Order Tracking Center ledger view
  - Enforce explicit try/except validation guardrails rejecting unselected line modifications

Coding standard: PEP 8 (https://python.org)
"""

import tkinter as tk
from tkinter import ttk, messagebox

class OrderSystemWindow(tk.Frame):
    """
    Embedded user interface frame component incorporating Customer shopping cart 
    actions and role-adaptive order history tracking ledgers.
    """
    def __init__(self, parent, user_manager, catalogue_manager, order_manager):
        # Initialized as an embedded frame component to sit inside their sidebar layout
        super().__init__(parent)
        self.user_manager = user_manager
        self.catalogue_manager = catalogue_manager
        self.order_manager = order_manager
        
        session = self.user_manager.get_session()
        self.current_user_id = session["user_id"] if session else "GUEST"
        self.user_role = session["role"] if session else "Customer"
        
        self.default_address = ""
        if session:
            try:
                users_list = self.user_manager._load_users()
                user_obj = next((u for u in users_list if u.user_id == self.current_user_id), None)
                if user_obj and hasattr(user_obj, "address"):
                    self.default_address = user_obj.address
            except Exception:
                pass

        self._build_ui()

    def _build_ui(self):
        """Constructs split tab views dividing checkout paths from historic tracking tables."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.cart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cart_frame, text="🛒 My Shopping Cart")
        self._build_cart_tab()

        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📦 Order Tracking Center")
        self._build_history_tab()
        
        # Apply role-based access restrictions
        if self.user_role == "StoreManager":
            self.notebook.tab(0, state="disabled")
            self.notebook.select(1)

    # ── Cart Processing Panel Construction ──────────────────────────────────

    def _build_cart_tab(self):
        ttk.Label(self.cart_frame, text="Active Shopping Cart Items", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        # Expanded back to 5 columns to show unit prices and subtotals
        columns = ("id", "title", "qty", "price", "subtotal")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings", height=8)
        self.cart_tree.heading("id", text="Book ID")
        self.cart_tree.heading("title", text="Book Title")
        self.cart_tree.heading("qty", text="Quantity")
        self.cart_tree.heading("price", text="Unit Price")
        self.cart_tree.heading("subtotal", text="Subtotal")
        
        self.cart_tree.column("id", width=100, anchor="center")
        self.cart_tree.column("title", width=250, anchor="w")
        self.cart_tree.column("qty", width=80, anchor="center")
        self.cart_tree.column("price", width=100, anchor="center")
        self.cart_tree.column("subtotal", width=100, anchor="center")
        self.cart_tree.pack(fill="x", padx=10, pady=5)

        btn_frame = ttk.Frame(self.cart_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="➕ Increase Qty", command=lambda: self._modify_qty(1)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="➖ Decrease Qty", command=lambda: self._modify_qty(-1)).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="🗑️ Remove Item", command=self._remove_item).pack(side="left", padx=2)
        
        self.lbl_grand_total = ttk.Label(btn_frame, text="Grand Total: $0.00", font=("Arial", 11, "bold"))
        self.lbl_grand_total.pack(side="right", padx=10)

        addr_frame = ttk.LabelFrame(self.cart_frame, text=" Shipping & Delivery Parameters ")
        addr_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(addr_frame, text="Physical Delivery Address:").pack(anchor="w", padx=5, pady=2)
        self.txt_address = tk.Text(addr_frame, height=3, width=50)
        self.txt_address.pack(fill="x", padx=5, pady=5)
        self.txt_address.insert("1.0", self.default_address)

        ttk.Button(self.cart_frame, text="🏁 Execute Safe Checkout Process", command=self._process_checkout).pack(anchor="e", padx=10, pady=10)
        self._refresh_cart_display()

    def _refresh_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        cart_dict = self.order_manager.get_cart(self.current_user_id)
        total_accumulator = 0.0

        for book_id, cart_item in cart_dict.items():
            total_accumulator += cart_item.line_total()
            # Inserting 5 specific values to load the price rows cleanly
            self.cart_tree.insert(
                "", "end", 
                values=(cart_item.book_id, cart_item.title, cart_item.quantity, f"${cart_item.price:.2f}", f"${cart_item.line_total():.2f}")
            )
        self.lbl_grand_total.config(text=f"Grand Total (inc. GST): ${total_accumulator * 1.1:.2f}")

    def _modify_qty(self, amount):
        """Handles quantity changes, ensuring stock levels are maintained."""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please choose an item to modify.")
            return
            
        try:
            item_values = self.cart_tree.item(selected)["values"]
            book_id = item_values[0]
            success, msg = self.order_manager.add_to_cart(self.current_user_id, str(book_id), amount)
            if not success:
                messagebox.showerror("Stock Allocation Error", msg)
            self._refresh_cart_display()
        except Exception:
            messagebox.showwarning("Selection Required", "Please select a valid item from the list.")

    def _remove_item(self):
        """Completely purges a book from the shopping cart view window."""
        selected = self.cart_tree.selection()
        if not selected:
            return
            
        try:
            item_values = self.cart_tree.item(selected)["values"]
            book_id = item_values[0]
            self.order_manager.remove_from_cart(self.current_user_id, str(book_id))
            self._refresh_cart_display()
        except Exception:
            pass

    def _process_checkout(self):
        """Validates checkout fields, finishes orders, and prints an invoice summary."""
        addr_input = self.txt_address.get("1.0", "end-1c")
        if not addr_input.strip():
            messagebox.showerror("Validation Failure", "Checkout Blocked: Delivery parameters cannot be blank.")
            return

        success, order_id_or_msg = self.order_manager.checkout(self.current_user_id, addr_input)
        if success:
            messagebox.showinfo("Success", f"Payment processed successfully!\nOrder Created: {order_id_or_msg}")
            self.txt_address.delete("1.0", "end")
            self._refresh_cart_display()
            self._refresh_history_display()
        else:
            messagebox.showerror("Checkout Blocked", order_id_or_msg)

    # ── History Tracking Logs Construction ──────────────────────────────────

    def _build_history_tab(self):
        """Generates views to list order trails and provide administrative tracking workflows."""
        ttk.Label(self.history_frame, text="Historic Processing Ledger Systems", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        columns = ("order_id", "user", "total", "status", "timestamp", "invoice_id")
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=10)
        self.history_tree.heading("order_id", text="Order ID")
        self.history_tree.heading("user", text="Customer Name")
        self.history_tree.heading("total", text="Total Paid (inc GST)")
        self.history_tree.heading("status", text="Current Status")
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("invoice_id", text="Invoice Reference")
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.mgr_controls = ttk.LabelFrame(self.history_frame, text=" Administrative Workflow Pipelines ")
        if self.user_role == "StoreManager":
            self.mgr_controls.pack(fill="x", padx=10, pady=10)
            ttk.Label(self.mgr_controls, text="Update Progress Flag:").pack(side="left", padx=5, pady=5)
            self.cmb_status = ttk.Combobox(self.mgr_controls, values=self.order_manager.STATUS_FLOW, state="readonly")
            self.cmb_status.pack(side="left", padx=5, pady=5)
            self.cmb_status.set("Placed")
            
            # --- CRITICAL REPLACEMENT: Interactive Deselect Operational Protection Helper ---
            def clear_entire_selection():
                self.history_tree.selection_remove(self.history_tree.selection())
                self.history_tree.focus("")
                
            ttk.Button(self.mgr_controls, text="🔄 Deselect Order Row", command=clear_entire_selection).pack(side="left", padx=5)
            
            ttk.Button(self.mgr_controls, text="💾 Commit Milestone Change", command=self._commit_status_change).pack(side="left", padx=10)

        self._refresh_history_display()


    def _refresh_history_display(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        if self.user_role == "StoreManager":
            dataset = self.order_manager.get_all_orders_for_manager()
        else:
            dataset = self.order_manager.get_customer_order_history(self.current_user_id)

        for order in dataset:
            self.history_tree.insert("", "end", values=(order.order_id, order.customer_name, f"${order.total:.2f}", order.status, order.created_at, order.invoice_id))

    def _commit_status_change(self):
        selected = self.history_tree.selection()
        
        # CRITICAL VALIDATION CHECK: Enforce the warning popup if no row is selected
        if not selected or len(selected) == 0:
            messagebox.showwarning(
                "Target Unspecified", 
                "Validation Error: No active order row entry record was selected. Please select an order from the list first."
            )
            return
            
        # If we pass the check, extract the order ID safely
        item_values = self.history_tree.item(selected[0])["values"]
        if not item_values:
            messagebox.showwarning(
                "Target Unspecified", 
                "Validation Error: No active order row entry record was selected. Please select an order from the list first."
            )
            return
            
        order_id = item_values[0]
        target_status = self.cmb_status.get()
        
        success, msg = self.order_manager.update_order_status(str(order_id), target_status)
        if success:
            messagebox.showinfo("State Configured", msg)
            self._refresh_history_display()
        else:
            messagebox.showerror("Workflow Integrity Mismatch", msg)
