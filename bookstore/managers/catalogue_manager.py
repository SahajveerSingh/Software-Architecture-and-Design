"""
CatalogueManager [Class]

Responsibilities:
  - Add a new book to the catalogue (Store Manager only)
  - Update an existing book's details (Store Manager only)
  - Remove a book from the catalogue (Store Manager only)
  - Validate all inputs: no blank fields, price > 0, ISBN exactly 13 digits
  - Return a list of all books for browsing (any user, no login required)
  - Search books by title, author, or genre (case-insensitive)
  - Filter books by price range
  - Decrement stock when an order is placed (called by OrderManager)
  - Increment stock when a return is approved (called by ReturnManager)

Collaborators: Book, file_storage

Design notes:
  - Follows the Information Expert heuristic: CatalogueManager owns all
    book-related data and is therefore responsible for all book-related logic
  - InventoryController was merged into this class to maintain High Cohesion
  - All write operations validate inputs before touching storage

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""

import uuid

from models.book import Book
from managers import file_storage as storage

BOOKS_FILE = "books.json"


class CatalogueManager:
    """Manages the complete catalogue of books and all stock operations."""

    # ── Private helpers ──────────────────────────────────────────────────────

    def _load_books(self):
        """Load all books from storage and return as a list of Book objects."""
        raw = storage.load(BOOKS_FILE)
        return [Book.from_dict(d) for d in raw]

    def _save_books(self, books):
        """Serialise a list of Book objects and persist to storage."""
        storage.save(BOOKS_FILE, [b.to_dict() for b in books])

    @staticmethod
    def _validate_inputs(title, author, genre, isbn, price, stock_quantity):
        """
        Validate all book fields before add or update.

        Rules:
          - title, author, genre must not be blank
          - isbn must be exactly 13 numeric digits
          - price must be a positive number
          - stock_quantity must be a non-negative integer

        Returns: (True, "") on success or (False, reason) on failure.
        """
        if not title or not title.strip():
            return False, "Title cannot be empty."
        if not author or not author.strip():
            return False, "Author cannot be empty."
        if not genre or not genre.strip():
            return False, "Genre cannot be empty."

        isbn_clean = str(isbn).strip().replace("-", "").replace(" ", "")
        if not isbn_clean.isdigit() or len(isbn_clean) != 13:
            return False, "ISBN must be exactly 13 digits (numbers only)."

        try:
            price_val = float(price)
            if price_val <= 0:
                return False, "Price must be a positive number."
        except (ValueError, TypeError):
            return False, "Price must be a valid number."

        try:
            stock_val = int(stock_quantity)
            if stock_val < 0:
                return False, "Stock quantity cannot be negative."
        except (ValueError, TypeError):
            return False, "Stock quantity must be a whole number."

        return True, ""

    # ── Store Manager operations ─────────────────────────────────────────────

    def add_book(self, title, author, genre, isbn, price, stock_quantity):
        """
        Add a new book to the catalogue.

        Validates all fields and checks for duplicate ISBN before saving.

        Returns: (success: bool, message: str, book_id: str | None)
        """
        ok, msg = self._validate_inputs(
            title, author, genre, isbn, price, stock_quantity
        )
        if not ok:
            return False, msg, None

        isbn_clean = str(isbn).strip().replace("-", "").replace(" ", "")

        books = self._load_books()

        # Duplicate ISBN check
        if any(b.isbn == isbn_clean for b in books):
            return False, f"A book with ISBN {isbn_clean} already exists.", None

        new_book = Book(
            book_id=str(uuid.uuid4()),
            title=title.strip(),
            author=author.strip(),
            genre=genre.strip(),
            isbn=isbn_clean,
            price=float(price),
            stock_quantity=int(stock_quantity),
        )
        books.append(new_book)
        self._save_books(books)
        return True, f'"{new_book.title}" added to the catalogue.', new_book.book_id

    def update_book(self, book_id, title=None, author=None, genre=None,
                    isbn=None, price=None, stock_quantity=None):
        """
        Update one or more fields of an existing book.

        Only fields passed as non-None are updated.
        Validates any field that is being changed.

        Returns: (success: bool, message: str)
        """
        books = self._load_books()
        book = next((b for b in books if b.book_id == book_id), None)
        if book is None:
            return False, "Book not found."

        # Build effective values — use new value if provided, else keep existing
        eff_title  = title.strip()          if title          is not None else book.title
        eff_author = author.strip()         if author         is not None else book.author
        eff_genre  = genre.strip()          if genre          is not None else book.genre
        eff_isbn   = isbn                   if isbn           is not None else book.isbn
        eff_price  = price                  if price          is not None else book.price
        eff_stock  = stock_quantity         if stock_quantity is not None else book.stock_quantity

        ok, msg = self._validate_inputs(
            eff_title, eff_author, eff_genre, eff_isbn, eff_price, eff_stock
        )
        if not ok:
            return False, msg

        isbn_clean = str(eff_isbn).strip().replace("-", "").replace(" ", "")

        # Duplicate ISBN check (exclude the book being updated)
        if any(b.isbn == isbn_clean and b.book_id != book_id for b in books):
            return False, f"Another book with ISBN {isbn_clean} already exists."

        book.title          = eff_title
        book.author         = eff_author
        book.genre          = eff_genre
        book.isbn           = isbn_clean
        book.price          = float(eff_price)
        book.stock_quantity = int(eff_stock)

        self._save_books(books)
        return True, f'"{book.title}" has been updated.'

    def remove_book(self, book_id):
        """
        Remove a book from the catalogue by its book_id.

        Returns: (success: bool, message: str)
        """
        books = self._load_books()
        target = next((b for b in books if b.book_id == book_id), None)
        if target is None:
            return False, "Book not found."

        books = [b for b in books if b.book_id != book_id]
        self._save_books(books)
        return True, f'"{target.title}" has been removed from the catalogue.'

    # ── Browse and search (available to all users) ───────────────────────────

    def get_all_books(self):
        """Return a list of all Book objects in the catalogue."""
        return self._load_books()

    def search_books(self, query="", genre_filter=None,
                     min_price=None, max_price=None):
        """
        Search and filter the catalogue.

        Args:
            query        : Free-text search matched case-insensitively against
                           title, author, and genre. Empty string = match all.
            genre_filter : If provided, restrict results to this genre
                           (case-insensitive exact match).
            min_price    : If provided, exclude books cheaper than this value.
            max_price    : If provided, exclude books more expensive than this.

        Returns: list of Book objects matching all supplied criteria.
        """
        books = self._load_books()
        query_lower = query.strip().lower()

        results = []
        for book in books:
            # Text search across title, author, genre
            if query_lower:
                haystack = (
                    book.title.lower()
                    + book.author.lower()
                    + book.genre.lower()
                )
                if query_lower not in haystack:
                    continue

            # Genre filter
            if genre_filter and genre_filter.strip():
                if book.genre.lower() != genre_filter.strip().lower():
                    continue

            # Price range filter
            if min_price is not None:
                try:
                    if book.price < float(min_price):
                        continue
                except (ValueError, TypeError):
                    pass
            if max_price is not None:
                try:
                    if book.price > float(max_price):
                        continue
                except (ValueError, TypeError):
                    pass

            results.append(book)

        return results

    def get_genres(self):
        """Return a sorted list of unique genre strings in the catalogue."""
        books = self._load_books()
        return sorted({b.genre for b in books})

    def get_book_by_id(self, book_id):
        """Return the Book with the given book_id, or None if not found."""
        books = self._load_books()
        return next((b for b in books if b.book_id == book_id), None)

    # ── Stock operations (called by OrderManager / ReturnManager) ────────────

    def decrement_stock(self, book_id, quantity=1):
        """
        Decrease a book's stock by the given quantity.
        Called by OrderManager when an order is placed.

        Returns: (success: bool, message: str)
        """
        books = self._load_books()
        book = next((b for b in books if b.book_id == book_id), None)
        if book is None:
            return False, "Book not found."
        if book.stock_quantity < quantity:
            return False, f"Insufficient stock. Only {book.stock_quantity} left."
        book.stock_quantity -= quantity
        self._save_books(books)
        return True, "Stock updated."

    def increment_stock(self, book_id, quantity=1):
        """
        Increase a book's stock by the given quantity.
        Called by ReturnManager when a return is approved.

        Returns: (success: bool, message: str)
        """
        books = self._load_books()
        book = next((b for b in books if b.book_id == book_id), None)
        if book is None:
            return False, "Book not found."
        book.stock_quantity += quantity
        self._save_books(books)
        return True, "Stock restocked."

    # ── Seed helper (called by BookstoreApp at startup) ──────────────────────

    def seed_catalogue(self):
        """
        Populate books.json with sample data if the catalogue is empty.
        Called by BookstoreApp during system initialisation so the app
        is immediately usable without manual data entry.
        """
        if self._load_books():
            return  # Already has data — do nothing

        sample_books = [
            Book("", "The Great Gatsby", "F. Scott Fitzgerald",
                 "Classic Fiction", "9780743273565", 18.99, 12),
            Book("", "To Kill a Mockingbird", "Harper Lee",
                 "Classic Fiction", "9780061935466", 16.99, 8),
            Book("", "1984", "George Orwell",
                 "Dystopian Fiction", "9780451524935", 14.99, 20),
            Book("", "Sapiens", "Yuval Noah Harari",
                 "Non-Fiction", "9780062316097", 24.99, 15),
            Book("", "Atomic Habits", "James Clear",
                 "Self-Help", "9780735211292", 27.99, 18),
            Book("", "The Hitchhiker's Guide to the Galaxy",
                 "Douglas Adams", "Science Fiction", "9780345391803", 15.99, 10),
            Book("", "Dune", "Frank Herbert",
                 "Science Fiction", "9780441013593", 22.99, 7),
            Book("", "The Alchemist", "Paulo Coelho",
                 "Fiction", "9780062315007", 17.99, 14),
            Book("", "Educated", "Tara Westover",
                 "Memoir", "9780399590504", 21.99, 6),
            Book("", "Python Crash Course", "Eric Matthes",
                 "Technology", "9781593279288", 49.99, 0),
        ]

        books = []
        for b in sample_books:
            b.book_id = str(uuid.uuid4())
            books.append(b)

        self._save_books(books)