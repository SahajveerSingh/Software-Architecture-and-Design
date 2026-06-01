"""
main.py — Entry point for the Favourite Books Online Bookstore.

To run:
  python3 main.py

Default Store Manager credentials:
  Email:    admin@favouritebooks.com
  Password: Admin@123

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(__file__))

from bookstore_app import BookstoreApp
from managers.catalogue_manager import CatalogueManager
from ui.auth_ui import LoginWindow, RegisterWindow
from ui.main_window import MainWindow


def main():
    # ── Bootstrap ─────────────────────────────────────────────────────────────
    app = BookstoreApp()

    # Step 1 — CatalogueManager (Member 2)
    catalogue_manager = CatalogueManager()
    catalogue_manager.seed_catalogue()       # populate books.json if empty
    app.register_catalogue_manager(catalogue_manager)

    # Step 3 — OrderManager (Member 3 — uncomment when ready)
    # from managers.order_manager import OrderManager
    # app.register_order_manager(
    #     OrderManager(app.user_manager, app.catalogue_manager)
    # )

    # ── Tkinter root window ───────────────────────────────────────────────────
    root = tk.Tk()
    root.withdraw()
    root.title("Favourite Books")

    # ── Navigation callbacks ──────────────────────────────────────────────────

    def on_login_success(role):
        main_win = MainWindow(
            user_manager=app.user_manager,
            catalogue_manager=app.catalogue_manager,
            order_manager=app.order_manager,
        )
        main_win.protocol("WM_DELETE_WINDOW",
                          lambda: on_main_close(main_win))
        main_win.mainloop()

    def on_main_close(win):
        app.shutdown()
        win.destroy()
        show_login()

    def show_register():
        RegisterWindow(root, user_manager=app.user_manager,
                       on_back=show_login)

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