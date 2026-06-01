"""
main_window.py — Main navigation window shown after successful login.

Provides role-based sidebar navigation:
  Customer    : Browse Catalogue | My Orders | My Profile
  StoreManager: Manage Catalogue | All Orders | Statistics | My Profile

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import tkinter as tk
from tkinter import ttk

from ui.auth_ui import UpdateAccountWindow, ProfileWindow
from ui.catalogue_ui import CataloguePanel

# Palette
BG        = "#F7F9FC"
SIDEBAR   = "#1A3A5C"
PANEL     = "#FFFFFF"
MID_BLUE  = "#185FA5"
DARK_BLUE = "#1A3A5C"
GREY      = "#888888"

FONT_NAV  = ("Arial", 11)
FONT_HEAD = ("Arial", 14, "bold")
FONT_BODY = ("Arial", 11)


class MainWindow(tk.Tk):
    """
    Root application window — displayed after successful login.
    Provides role-based navigation sidebar and a content area.
    """

    def __init__(self, user_manager,
                 catalogue_manager=None, order_manager=None):
        super().__init__()
        self.user_manager      = user_manager
        self.catalogue_manager = catalogue_manager
        self.order_manager     = order_manager

        session = user_manager.get_session() or {}
        self.role      = session.get("role", "Customer")
        self.user_name = session.get("name", "User")

        self.title(f"Favourite Books  —  {self.user_name}")
        self.geometry("1280x760")
        self.minsize(1000, 600)
        self.configure(bg=BG)
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1280) // 2
        y = (self.winfo_screenheight() - 760)  // 2
        self.geometry(f"1280x760+{x}+{y}")

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self._sidebar = tk.Frame(self, bg=SIDEBAR, width=200)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        self._content = tk.Frame(self, bg=BG)
        self._content.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._show_home()

    def _build_sidebar(self):
        sb = self._sidebar

        tk.Label(sb, text="Favourite\nBooks", bg=SIDEBAR, fg="white",
                 font=("Arial", 15, "bold"), pady=18).pack(fill="x")
        tk.Frame(sb, bg="#2C5282", height=1).pack(fill="x")

        tk.Label(sb, text=f"Hi, {self.user_name.split()[0]}",
                 bg=SIDEBAR, fg="#A0AEC0", font=("Arial", 10),
                 pady=8).pack(fill="x", padx=14)
        tk.Label(sb, text=f"({self.role})",
                 bg=SIDEBAR, fg="#718096", font=("Arial", 9)).pack()
        tk.Frame(sb, bg="#2C5282", height=1).pack(fill="x", pady=6)

        for label, cmd in self._nav_items():
            tk.Button(sb, text=label, command=cmd,
                      bg=SIDEBAR, fg="white", font=FONT_NAV,
                      relief="flat", anchor="w", padx=18, pady=10,
                      cursor="hand2", activebackground="#2C5282",
                      activeforeground="white").pack(fill="x")

        tk.Frame(sb, bg=SIDEBAR).pack(fill="both", expand=True)
        tk.Frame(sb, bg="#2C5282", height=1).pack(fill="x")
        tk.Button(sb, text="Log Out", command=self._logout,
                  bg=SIDEBAR, fg="#FC8181", font=FONT_NAV,
                  relief="flat", anchor="w", padx=18, pady=10,
                  cursor="hand2").pack(fill="x")

    def _nav_items(self):
        common = [
            ("My Profile",     self._show_profile),
            ("Update Account", self._show_update_account),
        ]
        if self.role == "StoreManager":
            return [
                ("📚  Manage Catalogue", self._show_catalogue),
                ("📋  All Orders",       self._show_orders),
                ("📊  Statistics",       self._show_statistics),
            ] + common
        else:
            return [
                ("📚  Browse Catalogue", self._show_catalogue),
                ("🛒  My Cart / Orders", self._show_orders),
            ] + common

    # ── Content helpers ───────────────────────────────────────────────────────

    def _clear_content(self):
        """Safely destroy all content widgets, ignoring any errors."""
        for w in self._content.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

    def _content_frame(self, title):
        self._clear_content()
        frame = tk.Frame(self._content, bg=BG, padx=28, pady=24)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=title, bg=BG, font=FONT_HEAD,
                 fg=DARK_BLUE).pack(anchor="w", pady=(0, 16))
        return frame

    # ── Navigation handlers ───────────────────────────────────────────────────

    def _show_home(self):
        frame = self._content_frame("Welcome to Favourite Books")
        tk.Label(frame,
                 text=f"You are logged in as {self.user_name} ({self.role}).\n\n"
                      "Use the sidebar to navigate.",
                 bg=BG, font=FONT_BODY, fg="#374151",
                 justify="left").pack(anchor="w")

    def _show_catalogue(self):
        self._clear_content()
        if self.catalogue_manager is None:
            frame = tk.Frame(self._content, bg=BG, padx=28, pady=24)
            frame.pack(fill="both", expand=True)
            tk.Label(frame, text="Catalogue not yet loaded.",
                     bg=BG, font=FONT_BODY, fg=GREY).pack()
            return
        try:
            CataloguePanel(
                self._content,
                catalogue_manager=self.catalogue_manager,
                user_manager=self.user_manager,
            ).pack(fill="both", expand=True)
        except Exception as e:
            frame = tk.Frame(self._content, bg=BG, padx=28, pady=24)
            frame.pack(fill="both", expand=True)
            tk.Label(frame, text=f"Error loading catalogue: {e}",
                     bg=BG, font=FONT_BODY, fg="red").pack()

    def _show_orders(self):
        frame = self._content_frame(
            "All Orders" if self.role == "StoreManager" else "My Cart / Orders"
        )
        ph = tk.Frame(frame, bg=PANEL, relief="solid", bd=1,
                      padx=20, pady=30)
        ph.pack(fill="both", expand=True)
        tk.Label(ph,
                 text="Orders / Cart UI\n\n"
                      "This panel will be implemented by Member 3.",
                 bg=PANEL, font=FONT_BODY, fg=GREY,
                 justify="center").pack(expand=True)

    def _show_statistics(self):
        frame = self._content_frame("Sales Statistics")
        ph = tk.Frame(frame, bg=PANEL, relief="solid", bd=1,
                      padx=20, pady=30)
        ph.pack(fill="both", expand=True)
        tk.Label(ph,
                 text="Statistics UI\n\nStatisticsManager will be wired in once implemented.",
                 bg=PANEL, font=FONT_BODY, fg=GREY,
                 justify="center").pack(expand=True)

    def _show_profile(self):
        try:
            ProfileWindow(self, self.user_manager)
        except Exception:
            pass

    def _show_update_account(self):
        try:
            UpdateAccountWindow(self, self.user_manager,
                                on_done=self._refresh_title)
        except Exception:
            pass

    def _refresh_title(self):
        session = self.user_manager.get_session() or {}
        self.user_name = session.get("name", self.user_name)
        self.title(f"Favourite Books  —  {self.user_name}")

    def _logout(self):
        self.user_manager.logout()
        self.destroy()