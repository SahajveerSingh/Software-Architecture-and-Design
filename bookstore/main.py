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
# Forces Python to look at the exact directory where main.py sits
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.dirname(current_dir)) # Safety fallback for parent paths
sys.path.insert(0, os.path.dirname(__file__))

from bookstore.managers.order_manager import OrderManager
from bookstore_app import BookstoreApp
from managers.catalogue_manager import CatalogueManager


def main():
    # Bootstrap
    app = BookstoreApp()
    catalogue_manager = CatalogueManager()
    catalogue_manager.seed_catalogue()
    app.register_catalogue_manager(catalogue_manager)

#Backend initialization 
    from managers.order_manager import OrderManager
    order_manager = OrderManager(app.user_manager, catalogue_manager)
    app.register_order_manager(order_manager)

    _run_login(app)
   


def _run_login(app):
    import tkinter as tk
    from ui.auth_ui import LoginWindow, RegisterWindow
    from ui.main_window import MainWindow

    root = tk.Tk()
    root.withdraw()

    def on_login_success(role):
        root.destroy()
        _run_main(app)

    def on_register():
        for w in root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        RegisterWindow(
            root,
            user_manager=app.user_manager,
            on_back=on_back_to_login,
        )

    def on_back_to_login():
        for w in root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        LoginWindow(
            root,
            user_manager=app.user_manager,
            on_success=on_login_success,
            on_register=on_register,
        )

    LoginWindow(
        root,
        user_manager=app.user_manager,
        on_success=on_login_success,
        on_register=on_register,
    )

    root.mainloop()


def _run_main(app):
    import tkinter as tk
    from ui.main_window import MainWindow
    from ui.order_ui import OrderSystemWindow

    def on_close(win):
        app.shutdown()
        win.destroy()
        _run_login(app)

    main_win = MainWindow(
        user_manager=app.user_manager,
        catalogue_manager=app.catalogue_manager,
        order_manager=app.order_manager,
    )

   
    main_win.protocol("WM_DELETE_WINDOW",
                      lambda: on_close(main_win))
    main_win.mainloop()


if __name__ == "__main__":
    main()