"""
auth_ui.py — Tkinter GUI for all Account & Authentication screens.

Screens provided:
  - LoginWindow         : email + password login with lockout feedback
  - RegisterWindow      : full registration form with live per-field validation
  - UpdateAccountWindow : update name, address, and/or password
  - ProfileWindow       : read-only view of current account details

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import tkinter as tk
from tkinter import messagebox

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#F7F9FC"
PANEL     = "#FFFFFF"
MID_BLUE  = "#185FA5"
DARK_BLUE = "#1A3A5C"
RED       = "#C0392B"
GREEN     = "#0F6E56"
GREY      = "#888888"
BORDER    = "#D1D5DB"

FONT_TITLE  = ("Arial", 18, "bold")
FONT_LABEL  = ("Arial", 11)
FONT_SMALL  = ("Arial", 9)
FONT_BTN    = ("Arial", 11, "bold")
FONT_LINK   = ("Arial", 10, "underline")


def _btn(parent, text, command, bg=MID_BLUE, fg="white"):
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, font=FONT_BTN,
                     relief="flat", cursor="hand2",
                     padx=12, pady=6)


# ── LoginWindow ───────────────────────────────────────────────────────────────

class LoginWindow(tk.Toplevel):
    """
    Login screen — authenticates a user via UserManager.login().
    Calls on_success(role) on successful login.
    Calls on_register() when user clicks "Create Account".
    """

    def __init__(self, master, user_manager, on_success, on_register):
        super().__init__(master)
        self.user_manager = user_manager
        self.on_success = on_success
        self.on_register = on_register

        self.title("Favourite Books — Login")
        self.geometry("400x420")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._build()
        self.grab_set()
        self.focus_force()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 400) // 2
        y = (self.winfo_screenheight() - 420) // 2
        self.geometry(f"400x420+{x}+{y}")

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=40, pady=30)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Favourite Books", bg=BG,
                 font=("Arial", 20, "bold"), fg=DARK_BLUE).pack(pady=(0, 4))
        tk.Label(frame, text="Sign in to your account", bg=BG,
                 font=FONT_LABEL, fg=GREY).pack(pady=(0, 20))

        tk.Label(frame, text="Email address", bg=BG,
                 font=FONT_LABEL, fg="#111111").pack(anchor="w")
        self.email_entry = tk.Entry(frame, font=("Arial", 11),
                                    relief="solid", bd=1)
        self.email_entry.pack(fill="x", pady=(2, 8))

        tk.Label(frame, text="Password", bg=BG,
                 font=FONT_LABEL, fg="#111111").pack(anchor="w")
        self.pw_entry = tk.Entry(frame, font=("Arial", 11),
                                 relief="solid", bd=1, show="*")
        self.pw_entry.pack(fill="x", pady=(2, 4))

        self.msg_label = tk.Label(frame, text="", bg=BG,
                                  font=FONT_SMALL, fg=RED, wraplength=300)
        self.msg_label.pack(anchor="w", pady=(0, 10))

        _btn(frame, "Sign In", self._login).pack(fill="x", pady=(0, 10))

        tk.Label(frame, text="Don't have an account?", bg=BG,
                 font=FONT_SMALL, fg=GREY).pack()
        lnk = tk.Label(frame, text="Create Account", bg=BG,
                       font=FONT_LINK, fg=MID_BLUE, cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda _: self._go_register())

        self.pw_entry.bind("<Return>", lambda _: self._login())

    def _login(self):
        email = self.email_entry.get().strip()
        password = self.pw_entry.get()
        ok, msg, role = self.user_manager.login(email, password)
        if ok:
            self.destroy()
            self.on_success(role)
        else:
            self.msg_label.config(text=msg)
            self.pw_entry.delete(0, "end")

    def _go_register(self):
        self.destroy()
        self.on_register()


# ── RegisterWindow ────────────────────────────────────────────────────────────

class RegisterWindow(tk.Toplevel):
    """
    Registration screen — creates a new Customer account via
    UserManager.register(). Shows live per-field validation errors.
    """

    def __init__(self, master, user_manager, on_back):
        super().__init__(master)
        self.user_manager = user_manager
        self.on_back = on_back

        self.title("Favourite Books — Create Account")
        self.geometry("440x580")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._build()
        self.grab_set()
        self.focus_force()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 440) // 2
        y = (self.winfo_screenheight() - 580) // 2
        self.geometry(f"440x580+{x}+{y}")

    def _field(self, parent, label_text, show=None):
        """Create a labelled entry + inline error label. Returns (entry, err_label)."""
        tk.Label(parent, text=label_text, bg=BG, font=FONT_LABEL,
                 fg="#111111", anchor="w").pack(fill="x")
        entry = tk.Entry(parent, font=("Arial", 11), relief="solid",
                         bd=1, show=show or "")
        entry.pack(fill="x", pady=(2, 0))
        err = tk.Label(parent, text="", bg=BG, font=FONT_SMALL,
                       fg=RED, anchor="w")
        err.pack(fill="x", pady=(0, 6))
        return entry, err

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=36, pady=24)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Create Account", bg=BG,
                 font=FONT_TITLE, fg=DARK_BLUE).pack(pady=(0, 16))

        self.name_e,  self.name_err  = self._field(frame, "Full name")
        self.email_e, self.email_err = self._field(frame, "Email address")
        self.addr_e,  self.addr_err  = self._field(frame, "Delivery address")
        self.pw_e,    self.pw_err    = self._field(frame, "Password", show="*")
        self.pw2_e,   self.pw2_err   = self._field(frame, "Confirm password", show="*")

        self.submit_msg = tk.Label(frame, text="", bg=BG, font=FONT_SMALL,
                                   fg=RED, wraplength=340)
        self.submit_msg.pack(pady=(0, 8))

        _btn(frame, "Create Account", self._register).pack(fill="x", pady=(0, 8))

        lnk = tk.Label(frame, text="← Back to Login", bg=BG,
                       font=FONT_LINK, fg=MID_BLUE, cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda _: self._back())

    def _register(self):
        for lbl in (self.name_err, self.email_err, self.addr_err,
                    self.pw_err, self.pw2_err, self.submit_msg):
            lbl.config(text="")

        name    = self.name_e.get().strip()
        email   = self.email_e.get().strip()
        address = self.addr_e.get().strip()
        pw      = self.pw_e.get()
        pw2     = self.pw2_e.get()

        valid = True

        if not name:
            self.name_err.config(text="Name is required.")
            valid = False
        if not email:
            self.email_err.config(text="Email is required.")
            valid = False
        if not address:
            self.addr_err.config(text="Delivery address is required.")
            valid = False
        if not pw:
            self.pw_err.config(text="Password is required.")
            valid = False
        if pw and pw2 and pw != pw2:
            self.pw2_err.config(text="Passwords do not match.")
            valid = False

        if not valid:
            return

        ok, msg = self.user_manager.register(name, email, pw, address)
        if ok:
            messagebox.showinfo("Account Created",
                                "Your account has been created. Please log in.",
                                parent=self)
            self._back()
        else:
            self.submit_msg.config(text=msg)

    def _back(self):
        self.destroy()
        self.on_back()


# ── UpdateAccountWindow ───────────────────────────────────────────────────────

class UpdateAccountWindow(tk.Toplevel):
    """
    Update account screen — allows the logged-in user to change their
    name, address, and/or password via UserManager.update_account().
    """

    def __init__(self, master, user_manager, on_done=None):
        super().__init__(master)
        self.user_manager = user_manager
        self.on_done = on_done

        self.title("Update Account Details")
        self.geometry("420x480")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._build()
        self.grab_set()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 480) // 2
        self.geometry(f"420x480+{x}+{y}")

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=36, pady=24)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Update Account", bg=BG,
                 font=FONT_TITLE, fg=DARK_BLUE).pack(pady=(0, 4))
        tk.Label(frame, text="Leave a field blank to keep it unchanged.",
                 bg=BG, font=FONT_SMALL, fg=GREY).pack(pady=(0, 14))

        profile = self.user_manager.get_user_profile() or {}

        def field(lbl, default="", show=None):
            tk.Label(frame, text=lbl, bg=BG, font=FONT_LABEL,
                     anchor="w").pack(fill="x")
            e = tk.Entry(frame, font=("Arial", 11), relief="solid",
                         bd=1, show=show or "")
            e.insert(0, default)
            e.pack(fill="x", pady=(2, 8))
            return e

        self.name_e    = field("Full name", profile.get("name", ""))
        self.addr_e    = field("Delivery address", profile.get("address", ""))

        tk.Frame(frame, bg=BORDER, height=1).pack(fill="x", pady=4)
        tk.Label(frame, text="Change password (optional)",
                 bg=BG, font=("Arial", 10, "bold"), fg=GREY).pack(anchor="w")

        self.curr_pw_e = field("Current password", show="*")
        self.new_pw_e  = field("New password", show="*")

        self.msg = tk.Label(frame, text="", bg=BG, font=FONT_SMALL,
                            fg=RED, wraplength=320)
        self.msg.pack(pady=(0, 8))

        _btn(frame, "Save Changes", self._save).pack(fill="x")

    def _save(self):
        self.msg.config(text="")

        name    = self.name_e.get().strip() or None
        address = self.addr_e.get().strip() or None
        curr_pw = self.curr_pw_e.get() or None
        new_pw  = self.new_pw_e.get() or None

        ok, msg = self.user_manager.update_account(
            new_name=name,
            new_address=address,
            current_password=curr_pw,
            new_password=new_pw,
        )
        if ok:
            messagebox.showinfo("Saved", msg, parent=self)
            self.destroy()
            if self.on_done:
                self.on_done()
        else:
            self.msg.config(text=msg)


# ── ProfileWindow ─────────────────────────────────────────────────────────────

class ProfileWindow(tk.Toplevel):
    """
    Read-only profile view for the currently logged-in user.
    Displays name, email, address, and role.
    """

    def __init__(self, master, user_manager):
        super().__init__(master)
        self.user_manager = user_manager

        self.title("My Profile")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center()
        self._build()
        self.grab_set()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 420) // 2
        y = (self.winfo_screenheight() - 380) // 2
        self.geometry(f"420x380+{x}+{y}")

    def _build(self):
        frame = tk.Frame(self, bg=BG, padx=36, pady=24)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="My Profile", bg=BG,
                 font=FONT_TITLE, fg=DARK_BLUE).pack(pady=(0, 16))

        profile = self.user_manager.get_user_profile() or {}

        def row(label, value):
            tk.Label(frame, text=label, bg=BG, font=("Arial", 10, "bold"),
                     fg=GREY, anchor="w").pack(fill="x")
            # wraplength ensures long addresses wrap instead of clipping
            tk.Label(frame, text=value or "—", bg=BG, font=FONT_LABEL,
                     fg="#111111", anchor="w", wraplength=340,
                     justify="left").pack(fill="x", pady=(0, 10))

        row("Name",    profile.get("name", ""))
        row("Email",   profile.get("email", ""))
        row("Address", profile.get("address", ""))
        row("Role",    profile.get("role", ""))

        tk.Frame(frame, bg=BG, height=6).pack()  # spacer before button
        _btn(frame, "Close", self.destroy, bg="#6B7280").pack(fill="x")
