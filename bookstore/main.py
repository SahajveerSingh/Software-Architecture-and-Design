"""
main.py — Entry point for the Favourite Books Online Bookstore.

To run:
  python main.py

Default Store Manager credentials:
  Email:    admin@favouritebooks.com
  Password: Admin@123

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)

Author: Sahajveer Pratap Singh Bhatia
"""
import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

from bookstore_app import BookstoreApp
from ui.auth_ui import LoginWindow, RegisterWindow
from ui.main_window import MainWindow


def main():
    # Bootstrap — UserManager created and Store Manager seeded
    app = BookstoreApp()

    # Register other managers as members complete their code
    #
    # Member 1 — uncomment when catalogue_manager.py is ready:
    # from managers.catalogue_manager import CatalogueManager
    # app.register_catalogue_manager(CatalogueManager())
    #
    # Member 3 — uncomment when order_manager.py is ready:
    # from managers.order_manager import OrderManager
    # app.register_order_manager(
    #     OrderManager(app.user_manager, app.catalogue_manager)
    # )

    # Tkinter root window (hidden — acts as parent for Toplevel windows)
    root = tk.Tk()
    root.withdraw()
    root.title("Favourite Books")

    # Navigation callbacks

    def on_login_success(role):
        """Open the main window after successful login."""
        main_win = MainWindow(
            user_manager=app.user_manager,
            catalogue_manager=app.catalogue_manager,
            order_manager=app.order_manager,
        )
        main_win.protocol("WM_DELETE_WINDOW", lambda: on_main_close(main_win))
        main_win.mainloop()

    def on_main_close(win):
        """Log out and return to the login screen when main window is closed."""
        app.shutdown()
        win.destroy()
        show_login()

    def show_register():
        RegisterWindow(root, user_manager=app.user_manager, on_back=show_login)

    def show_login():
        LoginWindow(
            root,
            user_manager=app.user_manager,
            on_success=on_login_success,
            on_register=show_register,
        )

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
