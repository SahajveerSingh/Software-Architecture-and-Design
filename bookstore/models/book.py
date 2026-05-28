"""
Book [Data-Holder Class]

Responsibilities:
  - Store and provide access to book details (title, author, genre, ISBN, price)
  - Store and provide access to current stock quantity

Collaborators: None (pure data-holder — no behaviour)

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""


class Book:
    """Data-holder for a single book in the catalogue."""

    def __init__(self, book_id, title, author, genre,
                 isbn, price, stock_quantity):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.isbn = isbn
        self.price = float(price)
        self.stock_quantity = int(stock_quantity)

    def to_dict(self):
        """Serialise to dict for JSON persistence."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "isbn": self.isbn,
            "price": self.price,
            "stock_quantity": self.stock_quantity,
        }

    @staticmethod
    def from_dict(data):
        """Deserialise from a dict loaded from JSON storage."""
        return Book(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            genre=data["genre"],
            isbn=data["isbn"],
            price=data["price"],
            stock_quantity=data["stock_quantity"],
        )
