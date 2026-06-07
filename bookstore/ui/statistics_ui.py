"""
statistics_ui.py — Tkinter UI panel for Sales Statistics.

Panel provided:
  - StatisticsPanel : Embedded panel loaded into MainWindow content area.
                      Only accessible to Store Manager role.
                      Shows revenue, order count, best sellers, status
                      breakdown, and recent orders table.

Coding standard: PEP 8 (https://peps.python.org/pep-0008/)
"""
import tkinter as tk
from tkinter import ttk

from managers.statistics_manager import StatisticsManager

# ── Palette (matches rest of app) ────────────────────────────────────────────
BG        = "#F7F9FC"
PANEL     = "#FFFFFF"
MID_BLUE  = "#185FA5"
DARK_BLUE = "#1A3A5C"
GREEN     = "#0F6E56"
GREY      = "#888888"
BORDER    = "#D1D5DB"
RED       = "#C0392B"

FONT_HEAD  = ("Arial", 15, "bold")
FONT_SUB   = ("Arial", 12, "bold")
FONT_BODY  = ("Arial", 11)
FONT_SMALL = ("Arial", 10)
FONT_BTN   = ("Arial", 11, "bold")
FONT_NUM   = ("Arial", 18, "bold")


class StatisticsPanel(tk.Frame):
    """
    Statistics panel embedded in MainWindow content area.
    Accessible to Store Manager only.
    """

    PERIODS = [
        ("Today",        "today"),
        ("Last 7 Days",  "week"),
        ("Last 30 Days", "month"),
        ("Last 365 Days","year"),
        ("All Time",     "all"),
    ]

    def __init__(self, parent, catalogue_manager=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.sm = StatisticsManager(catalogue_manager)
        self._period = "all"
        self._build()
        self._refresh()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # ── Top bar ───────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=BG, padx=20, pady=12)
        top.pack(fill="x")

        tk.Label(top, text="Sales Statistics", bg=BG,
                 font=FONT_HEAD, fg=DARK_BLUE).pack(side="left")

        # Period selector on the right
        period_frame = tk.Frame(top, bg=BG)
        period_frame.pack(side="right")

        tk.Label(period_frame, text="Period:", bg=BG,
                 font=FONT_BODY, fg=GREY).pack(side="left", padx=(0, 6))

        self._period_var = tk.StringVar(value="all")
        for label, value in self.PERIODS:
            tk.Radiobutton(
                period_frame, text=label, variable=self._period_var,
                value=value, bg=BG, font=FONT_SMALL,
                command=self._on_period_change,
                activebackground=BG, cursor="hand2",
            ).pack(side="left", padx=4)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Summary cards ─────────────────────────────────────────────────────
        cards_frame = tk.Frame(self, bg=BG, padx=20, pady=14)
        cards_frame.pack(fill="x")

        self._revenue_card  = self._make_card(cards_frame, "Total Revenue",      "$0.00",  GREEN)
        self._orders_card   = self._make_card(cards_frame, "Orders Placed",       "0",      MID_BLUE)
        self._avg_card      = self._make_card(cards_frame, "Avg Order Value",     "$0.00",  DARK_BLUE)

        # ── Bottom area: best sellers + status + recent orders ────────────────
        bottom = tk.Frame(self, bg=BG, padx=20, pady=4)
        bottom.pack(fill="both", expand=True)
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)

        # Left: recent orders table
        left = tk.Frame(bottom, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        tk.Label(left, text="Recent Orders", bg=BG,
                 font=FONT_SUB, fg=DARK_BLUE).grid(row=0, column=0,
                 sticky="w", pady=(0, 6))

        cols = ("Order ID", "Customer", "Total", "Status", "Date")
        style = ttk.Style()
        style.configure("Stats.Treeview", font=("Arial", 10), rowheight=26)
        style.configure("Stats.Treeview.Heading", font=("Arial", 10, "bold"))

        self._orders_tree = ttk.Treeview(
            left, columns=cols, show="headings",
            height=12, style="Stats.Treeview",
        )
        widths = {"Order ID": 110, "Customer": 130,
                  "Total": 90, "Status": 100, "Date": 140}
        for c in cols:
            self._orders_tree.heading(c, text=c)
            self._orders_tree.column(c, width=widths[c], minwidth=60, stretch=True)

        vsb = ttk.Scrollbar(left, orient="vertical",
                            command=self._orders_tree.yview)
        self._orders_tree.configure(yscrollcommand=vsb.set)
        self._orders_tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        # Status colour tags
        self._orders_tree.tag_configure("Delivered",  foreground=GREEN)
        self._orders_tree.tag_configure("Dispatched", foreground=MID_BLUE)
        self._orders_tree.tag_configure("Paid",       foreground=DARK_BLUE)
        self._orders_tree.tag_configure("Placed",     foreground="#D97706")

        # Right: best sellers + status breakdown
        right = tk.Frame(bottom, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        # Best sellers
        tk.Label(right, text="Top 5 Best Sellers", bg=BG,
                 font=FONT_SUB, fg=DARK_BLUE).pack(anchor="w", pady=(0, 6))

        self._bs_frame = tk.Frame(right, bg=PANEL, relief="solid",
                                  bd=1, padx=14, pady=10)
        self._bs_frame.pack(fill="x", pady=(0, 14))

        # Status breakdown
        tk.Label(right, text="Orders by Status", bg=BG,
                 font=FONT_SUB, fg=DARK_BLUE).pack(anchor="w", pady=(0, 6))

        self._status_frame = tk.Frame(right, bg=PANEL, relief="solid",
                                      bd=1, padx=14, pady=10)
        self._status_frame.pack(fill="x")

    def _make_card(self, parent, label, value, colour):
        """Create a summary metric card. Returns the value label for later updates."""
        card = tk.Frame(parent, bg=PANEL, relief="solid", bd=1,
                        padx=20, pady=16)
        card.pack(side="left", expand=True, fill="both", padx=(0, 12))

        tk.Label(card, text=label, bg=PANEL, font=FONT_SMALL,
                 fg=GREY).pack(anchor="w")
        val_lbl = tk.Label(card, text=value, bg=PANEL,
                           font=FONT_NUM, fg=colour)
        val_lbl.pack(anchor="w", pady=(4, 0))
        return val_lbl

    # ── Data refresh ──────────────────────────────────────────────────────────

    def _on_period_change(self):
        self._period = self._period_var.get()
        self._refresh()

    def _refresh(self):
        """Reload all statistics for the current period."""
        summary  = self.sm.get_summary(self._period)
        orders   = self.sm.get_recent_orders(self._period)
        statuses = self.sm.get_status_breakdown(self._period)

        # Update summary cards
        self._revenue_card.config(text=f"${summary['total_revenue']:,.2f}")
        self._orders_card.config(text=str(summary['order_count']))
        self._avg_card.config(text=f"${summary['avg_order_value']:,.2f}")

        # Update recent orders table
        self._orders_tree.delete(*self._orders_tree.get_children())
        for o in orders:
            self._orders_tree.insert(
                "", "end",
                values=(o.order_id, o.customer_name,
                        f"${o.total:.2f}", o.status, o.created_at),
                tags=(o.status,),
            )

        # Update best sellers
        for w in self._bs_frame.winfo_children():
            w.destroy()
        best = summary["best_sellers"]
        if best:
            for rank, (title, qty) in enumerate(best, 1):
                row = tk.Frame(self._bs_frame, bg=PANEL)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"{rank}.", bg=PANEL,
                         font=FONT_SMALL, fg=GREY, width=3).pack(side="left")
                tk.Label(row, text=title, bg=PANEL,
                         font=FONT_SMALL, fg="#111111",
                         anchor="w").pack(side="left", expand=True, fill="x")
                tk.Label(row, text=f"{qty} sold", bg=PANEL,
                         font=FONT_SMALL, fg=MID_BLUE).pack(side="right")
        else:
            tk.Label(self._bs_frame, text="No sales data yet.",
                     bg=PANEL, font=FONT_SMALL, fg=GREY).pack(anchor="w")

        # Update status breakdown
        for w in self._status_frame.winfo_children():
            w.destroy()
        status_colours = {
            "Delivered":  GREEN,
            "Dispatched": MID_BLUE,
            "Paid":       DARK_BLUE,
            "Placed":     "#D97706",
        }
        all_statuses = ["Placed", "Paid", "Dispatched", "Delivered"]
        for status in all_statuses:
            count = statuses.get(status, 0)
            row = tk.Frame(self._status_frame, bg=PANEL)
            row.pack(fill="x", pady=3)
            colour = status_colours.get(status, GREY)
            tk.Label(row, text="●", bg=PANEL,
                     font=FONT_SMALL, fg=colour).pack(side="left", padx=(0, 6))
            tk.Label(row, text=status, bg=PANEL,
                     font=FONT_SMALL, fg="#111111",
                     anchor="w").pack(side="left", expand=True, fill="x")
            tk.Label(row, text=str(count), bg=PANEL,
                     font=("Arial", 10, "bold"),
                     fg=colour).pack(side="right")
