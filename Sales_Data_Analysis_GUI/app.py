import os
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "data", "sales_data.csv")


class SalesDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales Data Analysis Dashboard")
        self.root.geometry("1250x800")
        self.root.minsize(1000, 650)

        self.bg = "#f4f6f8"
        self.card = "#ffffff"
        self.text = "#1f2937"
        self.accent = "#2563eb"

        self.root.configure(bg=self.bg)

        self.load_data()
        self.create_header()
        self.create_summary_cards()
        self.create_controls()
        self.create_chart_area()

        self.show_monthly_sales()

    def load_data(self):
        if not os.path.exists(CSV_FILE):
            messagebox.showerror(
                "File Not Found",
                f"Could not find:\n{CSV_FILE}\n\n"
                "Make sure data/sales_data.csv exists."
            )
            self.root.destroy()
            return

        self.data = pd.read_csv(CSV_FILE)

        required = {"Date", "Product", "Category", "Quantity", "Unit_Price"}
        missing = required - set(self.data.columns)

        if missing:
            messagebox.showerror(
                "Invalid CSV",
                "Missing columns: " + ", ".join(sorted(missing))
            )
            self.root.destroy()
            return

        self.data["Date"] = pd.to_datetime(self.data["Date"])
        self.data["Quantity"] = pd.to_numeric(self.data["Quantity"])
        self.data["Unit_Price"] = pd.to_numeric(self.data["Unit_Price"])
        self.data["Total_Sales"] = (
            self.data["Quantity"] * self.data["Unit_Price"]
        )

        self.data["Month"] = self.data["Date"].dt.strftime("%b")

        self.month_order = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]

    def create_header(self):
        header = tk.Frame(self.root, bg=self.accent, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="SALES DATA ANALYSIS DASHBOARD",
            font=("Segoe UI", 24, "bold"),
            bg=self.accent,
            fg="white"
        )
        title.pack(pady=20)

    def create_summary_cards(self):
        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack(fill="x", padx=20, pady=15)

        total_sales = self.data["Total_Sales"].sum()
        total_quantity = self.data["Quantity"].sum()

        product_quantity = self.data.groupby("Product")["Quantity"].sum()
        best_product = product_quantity.idxmax()

        monthly_sales = self.get_monthly_sales()
        best_month = monthly_sales.idxmax()

        cards = [
            ("TOTAL SALES", f"₹{total_sales:,.0f}"),
            ("TOTAL QUANTITY", f"{total_quantity:,}"),
            ("BEST PRODUCT", best_product),
            ("BEST MONTH", best_month),
        ]

        for title, value in cards:
            card = tk.Frame(
                frame,
                bg=self.card,
                highlightbackground="#d1d5db",
                highlightthickness=1
            )
            card.pack(side="left", expand=True, fill="both", padx=7)

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 10, "bold"),
                bg=self.card,
                fg="#6b7280"
            ).pack(pady=(15, 5))

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 18, "bold"),
                bg=self.card,
                fg=self.text
            ).pack(pady=(0, 15))

    def create_controls(self):
        controls = tk.Frame(self.root, bg=self.bg)
        controls.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            controls,
            text="View Analysis:",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg,
            fg=self.text
        ).pack(side="left", padx=(0, 10))

        ttk.Button(
            controls,
            text="Monthly Sales",
            command=self.show_monthly_sales
        ).pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Best Selling Products",
            command=self.show_best_products
        ).pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Product Pie Chart",
            command=self.show_pie_chart
        ).pack(side="left", padx=5)

        ttk.Button(
            controls,
            text="Refresh",
            command=self.refresh_dashboard
        ).pack(side="right", padx=5)

    def create_chart_area(self):
        self.chart_frame = tk.Frame(
            self.root,
            bg=self.card,
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        self.chart_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

    def get_monthly_sales(self):
        monthly = (
            self.data.groupby("Month")["Total_Sales"]
            .sum()
            .reindex(self.month_order)
            .fillna(0)
        )
        return monthly

    def clear_chart(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        plt.close("all")

    def display_figure(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_monthly_sales(self):
        self.clear_chart()

        monthly = self.get_monthly_sales()

        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.bar(monthly.index, monthly.values)

        ax.set_title(
            "Monthly Sales Analysis",
            fontsize=18,
            fontweight="bold"
        )
        ax.set_xlabel("Month")
        ax.set_ylabel("Sales (₹)")
        ax.grid(axis="y", alpha=0.25)

        for i, value in enumerate(monthly.values):
            ax.text(
                i,
                value,
                f"₹{value:,.0f}",
                ha="center",
                va="bottom",
                fontsize=8
            )

        fig.tight_layout()
        self.display_figure(fig)

    def show_best_products(self):
        self.clear_chart()

        products = (
            self.data.groupby("Product")["Quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.bar(products.index, products.values)

        ax.set_title(
            "Best Selling Products",
            fontsize=18,
            fontweight="bold"
        )
        ax.set_xlabel("Product")
        ax.set_ylabel("Quantity Sold")
        ax.grid(axis="y", alpha=0.25)

        for i, value in enumerate(products.values):
            ax.text(
                i,
                value,
                str(int(value)),
                ha="center",
                va="bottom",
                fontsize=10
            )

        fig.tight_layout()
        self.display_figure(fig)

    def show_pie_chart(self):
        self.clear_chart()

        sales = (
            self.data.groupby("Product")["Total_Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.pie(
            sales.values,
            labels=sales.index,
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title(
            "Product Sales Distribution",
            fontsize=18,
            fontweight="bold"
        )

        fig.tight_layout()
        self.display_figure(fig)

    def refresh_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.load_data()
        self.create_header()
        self.create_summary_cards()
        self.create_controls()
        self.create_chart_area()
        self.show_monthly_sales()


if __name__ == "__main__":
    root = tk.Tk()
    app = SalesDashboard(root)
    root.mainloop()
