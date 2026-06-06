"""
catalogue_ui.py - Tkinter UI panel for all Catalogue screens.

Panels provided:
  - CataloguePanel : Embedded panel loaded into MainWindow content area.
                     Switches view based on user role:
                       StoreManager -> Manage Catalogue (add / edit / remove + browse)
                       Customer     -> Browse Catalogue (search / filter / view / add to cart)

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Palette
BG        = "#F7F9FC"
PANEL     = "#FFFFFF"
MID_BLUE  = "#185FA5"
DARK_BLUE = "#1A3A5C"
RED       = "#C0392B"
ORANGE    = "#D97706"
GREEN     = "#0F6E56"
GREY      = "#888888"

FONT_HEAD  = ("Arial", 15, "bold")
FONT_SUB   = ("Arial", 12, "bold")
FONT_BODY  = ("Arial", 12)
FONT_SMALL = ("Arial", 10)
FONT_BTN   = ("Arial", 11, "bold")


def _safe_iid(book_id):
    """Prefix book_id with 'b_' so Treeview row IDs never start with a digit."""
    return f"b_{book_id}"


def _strip_iid(iid):
    """Strip the 'b_' prefix to recover the real book_id."""
    return iid[2:] if iid.startswith("b_") else iid


class CataloguePanel(tk.Frame):
    """
    Main catalogue panel embedded in MainWindow content area.
    Renders differently for StoreManager vs Customer.
    """

    def __init__(self, parent, catalogue_manager, user_manager,
                 cart=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.cm   = catalogue_manager
        self.um   = user_manager
        # cart is a list of dicts: [{"book_id": ..., "quantity": ...}]
        # passed in by OrderManager when available, empty list otherwise
        self.cart = cart if cart is not None else []
        session   = user_manager.get_session() or {}
        self.role = session.get("role", "Customer")
        self._selected_book_id = None
        self._editing_id       = None
        self._build()

    def _build(self):
        if self.role == "StoreManager":
            self._build_manager_view()
        else:
            self._build_customer_view()

    # STORE MANAGER VIEW

    def _build_manager_view(self):
        # Top bar
        top = tk.Frame(self, bg=BG, pady=10, padx=20)
        top.pack(fill="x")
        tk.Label(top, text="Manage Catalogue", bg=BG,
                 font=FONT_HEAD, fg=DARK_BLUE).pack(side="left")

        # Search bar
        search_bar = tk.Frame(self, bg=BG, padx=20, pady=6)
        search_bar.pack(fill="x")

        tk.Label(search_bar, text="Search:", bg=BG,
                 font=FONT_BODY).pack(side="left")

        self._mgr_search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_bar,
            textvariable=self._mgr_search_var,
            font=FONT_BODY,
            relief="solid",
            bd=1,
            width=30,
        )
        search_entry.pack(side="left", padx=(6, 10))
        search_entry.bind("<Return>", lambda e: self._mgr_do_search())

        tk.Button(
            search_bar,
            text="Search",
            command=self._mgr_do_search,
            bg=MID_BLUE, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=8, state="normal",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            search_bar,
            text="Show All",
            command=self._mgr_show_all,
            bg="#6B7280", fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=9, state="normal",
        ).pack(side="left")

        # Main area
        main = tk.Frame(self, bg=BG, padx=20, pady=8)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        # Left: book table
        left = tk.Frame(main, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Catalogue.Treeview",
                        font=("Arial", 11), rowheight=28)
        style.configure("Catalogue.Treeview.Heading",
                        font=("Arial", 11, "bold"))

        cols = ("Title", "Author", "Genre", "ISBN", "Price", "Stock")
        self._mgr_tree = ttk.Treeview(
            left, columns=cols, show="headings",
            selectmode="browse", height=16,
            style="Catalogue.Treeview",
        )
        col_widths = {"Title": 180, "Author": 140, "Genre": 110,
                      "ISBN": 120, "Price": 70, "Stock": 55}
        for c in cols:
            self._mgr_tree.heading(c, text=c)
            self._mgr_tree.column(c, width=col_widths[c],
                                  minwidth=50, stretch=True)

        vsb = ttk.Scrollbar(left, orient="vertical",
                            command=self._mgr_tree.yview)
        self._mgr_tree.configure(yscrollcommand=vsb.set)
        self._mgr_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._mgr_tree.bind("<<TreeviewSelect>>", self._mgr_on_select)

        # Buttons under table
        btn_row = tk.Frame(left, bg=BG, pady=8)
        btn_row.grid(row=1, column=0, columnspan=2, sticky="w")

        tk.Button(
            btn_row, text="Edit Selected",
            command=self._mgr_load_for_edit,
            bg=MID_BLUE, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=15, state="normal",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_row, text="Remove Selected",
            command=self._mgr_remove_selected,
            bg=RED, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=16, state="normal",
        ).pack(side="left")

        # Right: add/edit form
        right = tk.Frame(main, bg=PANEL, relief="solid", bd=1,
                         padx=18, pady=18)
        right.grid(row=0, column=1, sticky="nsew")

        self._form_title_label = tk.Label(
            right, text="Add New Book",
            bg=PANEL, font=FONT_SUB, fg=DARK_BLUE,
        )
        self._form_title_label.pack(anchor="w", pady=(0, 12))

        self._entries = {}

        def field(key, label):
            tk.Label(right, text=label, bg=PANEL,
                     font=("Arial", 11), fg="#333",
                     anchor="w").pack(fill="x")
            e = tk.Entry(right, font=FONT_BODY, relief="solid", bd=1)
            e.pack(fill="x", pady=(2, 10))
            self._entries[key] = e

        field("title",  "Title *")
        field("author", "Author *")
        field("genre",  "Genre *")
        field("isbn",   "ISBN (13 digits) *")
        field("price",  "Price (AUD) *")
        field("stock",  "Stock Quantity *")

        self._form_msg = tk.Label(
            right, text="", bg=PANEL,
            font=FONT_SMALL, fg=RED,
            wraplength=240, justify="left",
        )
        self._form_msg.pack(anchor="w", pady=(0, 8))

        form_btns = tk.Frame(right, bg=PANEL)
        form_btns.pack(fill="x")

        self._save_btn = tk.Button(
            form_btns, text="Save Book",
            command=self._mgr_save_book,
            bg=MID_BLUE, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=12, state="normal",
        )
        self._save_btn.pack(side="left", padx=(0, 8))

        tk.Button(
            form_btns, text="Clear",
            command=self._mgr_clear_form,
            bg="#6B7280", fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=8, state="normal",
        ).pack(side="left")

        self._mgr_refresh_table()

    def _mgr_refresh_table(self, books=None):
        if books is None:
            books = self.cm.get_all_books()
        self._mgr_tree.delete(*self._mgr_tree.get_children())
        for book in books:
            tag = "outofstock" if book.stock_quantity == 0 else ""
            self._mgr_tree.insert(
                "", "end",
                iid=_safe_iid(book.book_id),
                values=(book.title, book.author, book.genre,
                        book.isbn, f"${book.price:.2f}",
                        book.stock_quantity),
                tags=(tag,),
            )
        self._mgr_tree.tag_configure("outofstock", foreground=ORANGE)

    def _mgr_do_search(self):
        q = self._mgr_search_var.get().strip()
        results = self.cm.search_books(query=q)
        self._mgr_refresh_table(results)

    def _mgr_show_all(self):
        self._mgr_search_var.set("")
        self._mgr_refresh_table()

    def _mgr_on_select(self, _event=None):
        sel = self._mgr_tree.selection()
        self._selected_book_id = _strip_iid(sel[0]) if sel else None

    def _mgr_load_for_edit(self):
        if not self._selected_book_id:
            messagebox.showwarning(
                "No Selection",
                "Please click a book row to select it first.",
                parent=self,
            )
            return
        book = self.cm.get_book_by_id(self._selected_book_id)
        if not book:
            messagebox.showerror("Error", "Book not found.", parent=self)
            return
        self._editing_id = book.book_id
        self._form_title_label.config(text="Edit Book")
        self._set_entry("title",  book.title)
        self._set_entry("author", book.author)
        self._set_entry("genre",  book.genre)
        self._set_entry("isbn",   book.isbn)
        self._set_entry("price",  str(book.price))
        self._set_entry("stock",  str(book.stock_quantity))
        self._form_msg.config(text="")
        self._save_btn.config(text="Update Book")

    def _set_entry(self, key, value):
        e = self._entries[key]
        e.delete(0, tk.END)
        e.insert(0, value)

    def _get_entry(self, key):
        return self._entries[key].get()

    def _mgr_save_book(self):
        self._form_msg.config(text="")
        title  = self._get_entry("title")
        author = self._get_entry("author")
        genre  = self._get_entry("genre")
        isbn   = self._get_entry("isbn")
        price  = self._get_entry("price")
        stock  = self._get_entry("stock")

        if self._editing_id:
            ok, msg = self.cm.update_book(
                self._editing_id,
                title=title, author=author, genre=genre,
                isbn=isbn, price=price, stock_quantity=stock,
            )
            if ok:
                messagebox.showinfo("Updated", msg, parent=self)
                self._mgr_clear_form()
                self._mgr_refresh_table()
            else:
                self._form_msg.config(text=msg)
        else:
            ok, msg, _ = self.cm.add_book(
                title, author, genre, isbn, price, stock
            )
            if ok:
                messagebox.showinfo("Added", msg, parent=self)
                self._mgr_clear_form()
                self._mgr_refresh_table()
            else:
                self._form_msg.config(text=msg)

    def _mgr_remove_selected(self):
        if not self._selected_book_id:
            messagebox.showwarning(
                "No Selection",
                "Please click a book row to select it first.",
                parent=self,
            )
            return
        book = self.cm.get_book_by_id(self._selected_book_id)
        if not book:
            return
        confirm = messagebox.askyesno(
            "Confirm Remove",
            f'Remove "{book.title}" from the catalogue?\n\nThis cannot be undone.',
            parent=self,
        )
        if confirm:
            ok, msg = self.cm.remove_book(self._selected_book_id)
            if ok:
                messagebox.showinfo("Removed", msg, parent=self)
                self._selected_book_id = None
                self._mgr_clear_form()
                self._mgr_refresh_table()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _mgr_clear_form(self):
        self._editing_id = None
        self._form_title_label.config(text="Add New Book")
        self._save_btn.config(text="Save Book")
        for key in self._entries:
            self._entries[key].delete(0, tk.END)
        self._form_msg.config(text="")

    # CUSTOMER VIEW

    def _build_customer_view(self):
        # Top bar
        top = tk.Frame(self, bg=BG, pady=10, padx=20)
        top.pack(fill="x")
        tk.Label(top, text="Browse Catalogue", bg=BG,
                 font=FONT_HEAD, fg=DARK_BLUE).pack(side="left")

        # Cart count label
        self._cart_label = tk.Label(
            top, text=f"🛒  Cart: {len(self.cart)} item(s)",
            bg=BG, font=FONT_BODY, fg=MID_BLUE,
        )
        self._cart_label.pack(side="right", padx=20)

        # Filter bar
        filter_bar = tk.Frame(self, bg=BG, padx=20, pady=6)
        filter_bar.pack(fill="x")

        tk.Label(filter_bar, text="Search:", bg=BG,
                 font=FONT_BODY).pack(side="left")
        self._cust_search_var = tk.StringVar()
        cust_entry = tk.Entry(
            filter_bar,
            textvariable=self._cust_search_var,
            font=FONT_BODY, relief="solid", bd=1, width=22,
        )
        cust_entry.pack(side="left", padx=(6, 12))
        cust_entry.bind("<Return>", lambda e: self._cust_do_search())

        tk.Label(filter_bar, text="Genre:", bg=BG,
                 font=FONT_BODY).pack(side="left")
        self._cust_genre_var = tk.StringVar(value="All Genres")
        self._genre_combo = ttk.Combobox(
            filter_bar, textvariable=self._cust_genre_var,
            font=FONT_BODY, width=15, state="readonly",
        )
        self._genre_combo.pack(side="left", padx=(6, 12))

        tk.Label(filter_bar, text="Price $", bg=BG,
                 font=FONT_BODY).pack(side="left")
        self._cust_min_var = tk.StringVar()
        tk.Entry(
            filter_bar, textvariable=self._cust_min_var,
            font=FONT_BODY, relief="solid", bd=1, width=5,
        ).pack(side="left", padx=(6, 2))
        tk.Label(filter_bar, text="-", bg=BG,
                 font=FONT_BODY).pack(side="left")
        self._cust_max_var = tk.StringVar()
        tk.Entry(
            filter_bar, textvariable=self._cust_max_var,
            font=FONT_BODY, relief="solid", bd=1, width=5,
        ).pack(side="left", padx=(2, 12))

        tk.Button(
            filter_bar, text="Search",
            command=self._cust_do_search,
            bg=MID_BLUE, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=8, state="normal",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            filter_bar, text="Clear",
            command=self._cust_clear_filters,
            bg="#6B7280", fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=7, state="normal",
        ).pack(side="left")

        # Book list
        list_frame = tk.Frame(self, bg=BG, padx=20, pady=8)
        list_frame.pack(fill="both", expand=True)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Browse.Treeview",
                        font=("Arial", 12), rowheight=30)
        style.configure("Browse.Treeview.Heading",
                        font=("Arial", 12, "bold"))

        cols = ("Title", "Author", "Genre", "Price", "Availability")
        self._cust_tree = ttk.Treeview(
            list_frame, columns=cols, show="headings",
            selectmode="browse", height=14,
            style="Browse.Treeview",
        )
        col_widths = {"Title": 260, "Author": 180, "Genre": 130,
                      "Price": 80, "Availability": 140}
        for c in cols:
            self._cust_tree.heading(c, text=c)
            self._cust_tree.column(c, width=col_widths[c],
                                   minwidth=60, stretch=True)

        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                            command=self._cust_tree.yview)
        self._cust_tree.configure(yscrollcommand=vsb.set)
        self._cust_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self._cust_tree.tag_configure("outofstock", foreground=ORANGE)
        self._cust_tree.bind("<<TreeviewSelect>>", self._cust_on_select)

        # Bottom bar — status + Add to Cart button
        bottom = tk.Frame(self, bg=BG, padx=20, pady=8)
        bottom.pack(fill="x")

        self._cust_status = tk.Label(
            bottom, text="", bg=BG, font=FONT_SMALL, fg=GREY,
        )
        self._cust_status.pack(side="left")

        # Quantity selector
        tk.Label(bottom, text="Qty:", bg=BG,
                 font=FONT_BODY).pack(side="right", padx=(0, 4))
        self._qty_var = tk.StringVar(value="1")
        tk.Spinbox(
            bottom,
            from_=1, to=99,
            textvariable=self._qty_var,
            font=FONT_BODY, width=4,
            relief="solid", bd=1,
        ).pack(side="right", padx=(0, 8))

        # Add to Cart button
        self._add_cart_btn = tk.Button(
            bottom,
            text="🛒  Add to Cart",
            command=self._cust_add_to_cart,
            bg=GREEN, fg="white", font=FONT_BTN,
            relief="flat", cursor="hand2",
            padx=12, pady=6, width=14, state="normal",
        )
        self._add_cart_btn.pack(side="right", padx=(0, 8))

        self._cust_selected_book_id = None
        self._cust_refresh_genres()
        self._cust_refresh_table()

    def _cust_on_select(self, _event=None):
        sel = self._cust_tree.selection()
        self._cust_selected_book_id = _strip_iid(sel[0]) if sel else None

    def _cust_add_to_cart(self):
        """
        Add the selected book to the cart.
        - Checks a book is selected
        - Checks the book is in stock
        - If already in cart, increments quantity
        - If not in cart, adds new entry
        - Updates the cart label count
        - Shows confirmation message
        """
        if not self._cust_selected_book_id:
            messagebox.showwarning(
                "No Selection",
                "Please click a book to select it first.",
                parent=self,
            )
            return

        book = self.cm.get_book_by_id(self._cust_selected_book_id)
        if not book:
            messagebox.showerror("Error", "Book not found.", parent=self)
            return

        if book.stock_quantity == 0:
            messagebox.showwarning(
                "Out of Stock",
                f'"{book.title}" is currently out of stock.',
                parent=self,
            )
            return

        try:
            qty = int(self._qty_var.get())
            if qty < 1:
                qty = 1
        except ValueError:
            qty = 1

        if qty > book.stock_quantity:
            messagebox.showwarning(
                "Insufficient Stock",
                f'Only {book.stock_quantity} copy/copies of '
                f'"{book.title}" available.',
                parent=self,
            )
            return

        # Check if already in cart — increment if so
        for item in self.cart:
            if item["book_id"] == book.book_id:
                item["quantity"] += qty
                self._update_cart_label()
                messagebox.showinfo(
                    "Cart Updated",
                    f'"{book.title}" quantity updated to '
                    f'{item["quantity"]} in your cart.',
                    parent=self,
                )
                return

        # Not in cart — add new entry
        self.cart.append({
            "book_id":  book.book_id,
            "title":    book.title,
            "price":    book.price,
            "quantity": qty,
        })
        self._update_cart_label()
        messagebox.showinfo(
            "Added to Cart",
            f'"{book.title}" (x{qty}) has been added to your cart.',
            parent=self,
        )

    def _update_cart_label(self):
        total_items = sum(i["quantity"] for i in self.cart)
        self._cart_label.config(
            text=f"🛒  Cart: {total_items} item(s)"
        )

    def _cust_refresh_genres(self):
        genres = ["All Genres"] + self.cm.get_genres()
        self._genre_combo["values"] = genres
        self._cust_genre_var.set("All Genres")

    def _cust_refresh_table(self, books=None):
        if books is None:
            books = self.cm.get_all_books()
        self._cust_tree.delete(*self._cust_tree.get_children())
        for book in books:
            if book.stock_quantity > 0:
                avail = f"In Stock ({book.stock_quantity})"
                tag = ""
            else:
                avail = "[OUT OF STOCK]"
                tag = "outofstock"
            self._cust_tree.insert(
                "", "end",
                iid=_safe_iid(book.book_id),
                values=(book.title, book.author, book.genre,
                        f"${book.price:.2f}", avail),
                tags=(tag,),
            )
        count = len(books)
        self._cust_status.config(
            text=f"{count} book{'s' if count != 1 else ''} found."
        )

    def _cust_do_search(self):
        query = self._cust_search_var.get().strip()
        genre = self._cust_genre_var.get()
        genre_filter = None if genre == "All Genres" else genre
        min_p = self._cust_min_var.get().strip() or None
        max_p = self._cust_max_var.get().strip() or None

        for label, val in [("Min price", min_p), ("Max price", max_p)]:
            if val is not None:
                try:
                    float(val)
                except ValueError:
                    messagebox.showwarning(
                        "Invalid Filter",
                        f"{label} must be a number.",
                        parent=self,
                    )
                    return

        results = self.cm.search_books(
            query=query,
            genre_filter=genre_filter,
            min_price=min_p,
            max_price=max_p,
        )
        self._cust_refresh_table(results)

    def _cust_clear_filters(self):
        self._cust_search_var.set("")
        self._cust_genre_var.set("All Genres")
        self._cust_min_var.set("")
        self._cust_max_var.set("")
        self._cust_refresh_genres()
        self._cust_refresh_table()