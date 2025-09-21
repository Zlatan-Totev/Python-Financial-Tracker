import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv

import matplotlib.pyplot as plt

import db
import model

# Categories shown in the dropdowns
CATEGORIES = [
    "Income",
    "Rent",
    "Utilities",
    "Groceries",
    "Dining",
    "Transportation",
    "Healthcare",
    "Subscriptions",
    "Education",
    "Entertainment",
    "Vacation",
    "Other"
]

def refresh_table(tree):
    tree.delete(*tree.get_children())
    for tid, t_date, amount, category, desc in model.list_transactions(limit=5000):
        tree.insert("", "end", values=(tid, t_date, f"{amount:.2f}", category, desc))

def on_add(entry_date, entry_amount, combo_cat, entry_desc, tree):
    try:
        t_date = entry_date.get().strip()
        amount_str = entry_amount.get().strip()
        if not amount_str:
            raise ValueError("Amount is required.")
        amount = float(amount_str)
        category = combo_cat.get().strip() or "Other"
        description = entry_desc.get().strip()
        model.add_transaction(t_date, amount, category, description)
        refresh_table(tree)
        entry_amount.delete(0, tk.END); entry_desc.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Could not add transaction: {e}")

def on_delete(tree):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Delete", "Select at least one transaction to delete.")
        return
    if not messagebox.askyesno("Confirm", "Delete selected transaction(s)?"):
        return
    for item in sel:
        tid = int(tree.item(item, "values")[0])
        model.delete_transaction(tid)
    refresh_table(tree)

def parse_tree_row(item_values):
    tid = int(item_values[0])
    t_date = item_values[1]
    amount = float(item_values[2])
    category = item_values[3]
    desc = item_values[4]
    return tid, t_date, amount, category, desc

def on_edit(tree):
    sel = tree.selection()
    if not sel:
        messagebox.showinfo("Edit", "Select a transaction to edit.")
        return
    item = sel[0]
    values = tree.item(item, "values")
    open_edit_dialog(tree, values)

def on_tree_double_click(event, tree):
    item = tree.identify_row(event.y)
    if not item:
        return
    values = tree.item(item, "values")
    if not values:
        return
    open_edit_dialog(tree, values)

def open_edit_dialog(tree, item_values):
    tid, t_date, amount, category, desc = parse_tree_row(item_values)

    win = tk.Toplevel()
    win.title(f"Edit Transaction #{tid}")
    win.grab_set()

    ttk.Label(win, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    e_date = ttk.Entry(win, width=18); e_date.insert(0, t_date); e_date.grid(row=0, column=1, padx=6, pady=6)

    ttk.Label(win, text="Amount (+income, -expense):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
    e_amount = ttk.Entry(win, width=18); e_amount.insert(0, str(amount)); e_amount.grid(row=1, column=1, padx=6, pady=6)

    ttk.Label(win, text="Category:").grid(row=2, column=0, sticky="w", padx=6, pady=6)
    e_cat = ttk.Combobox(win, values=CATEGORIES, width=20)
    e_cat.set(category if category in CATEGORIES else "Other")
    e_cat.grid(row=2, column=1, padx=6, pady=6)

    ttk.Label(win, text="Description:").grid(row=3, column=0, sticky="w", padx=6, pady=6)
    e_desc = ttk.Entry(win, width=40); e_desc.insert(0, desc); e_desc.grid(row=3, column=1, padx=6, pady=6, sticky="we")

    def save_and_close():
        try:
            new_date = e_date.get().strip()
            new_amount = float(e_amount.get().strip())
            new_cat = e_cat.get().strip() or "Other"
            new_desc = e_desc.get().strip()
            model.update_transaction(tid, new_date, new_amount, new_cat, new_desc)
            refresh_table(tree)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not update: {e}")

    btn_frame = ttk.Frame(win); btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
    ttk.Button(btn_frame, text="Save", command=save_and_close).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="left", padx=6)

def plot_monthly(year_var, month_var):
    try:
        year = int(year_var.get()); month = int(month_var.get())
        data = model.monthly_totals(year, month)
        if not data:
            messagebox.showinfo("No data", "No transactions for that month."); return

        categories = list(data.keys()); totals = [data[c] for c in categories]
        plt.figure(); plt.title(f"Monthly Totals ({year}-{month:02d}) - Category Bar")
        plt.bar(categories, totals); plt.xticks(rotation=45, ha='right'); plt.tight_layout(); plt.show()

        expense_pairs = [(c, -v) for c, v in data.items() if v < 0]
        if expense_pairs:
            labels = [c for c, _ in expense_pairs]; sizes = [v for _, v in expense_pairs]
            plt.figure(); plt.title(f"Monthly Expenses by Category ({year}-{month:02d}) - Pie")
            plt.pie(sizes, labels=labels, autopct='%1.1f%%'); plt.tight_layout(); plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Could not plot monthly totals: {e}")

def plot_yearly(year_var):
    try:
        year = int(year_var.get())
        data = model.yearly_totals(year)
        if not data:
            messagebox.showinfo("No data", "No transactions for that year."); return

        categories = list(data.keys()); totals = [data[c] for c in categories]
        plt.figure(); plt.title(f"Yearly Totals ({year}) - Category Bar")
        plt.bar(categories, totals); plt.xticks(rotation=45, ha='right'); plt.tight_layout(); plt.show()

        expense_pairs = [(c, -v) for c, v in data.items() if v < 0]
        if expense_pairs:
            labels = [c for c, _ in expense_pairs]; sizes = [v for _, v in expense_pairs]
            plt.figure(); plt.title(f"Yearly Expenses by Category ({year}) - Pie")
            plt.pie(sizes, labels=labels, autopct='%1.1f%%'); plt.tight_layout(); plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Could not plot yearly totals: {e}")

def plot_monthly_split(year_var, month_var):
    try:
        year = int(year_var.get()); month = int(month_var.get())
        d = model.monthly_income_expense(year, month)
        inc, exp = d.get("Income", 0.0), d.get("Expense", 0.0)
        if inc == 0 and exp == 0:
            messagebox.showinfo("No data", "No transactions for that month."); return

        plt.figure(); plt.title(f"Monthly Income vs Expense ({year}-{month:02d}) - Bar")
        plt.bar(["Income","Expense"], [inc, exp]); plt.tight_layout(); plt.show()

        sizes = [v for v in [inc, exp] if v > 0]
        labels = [lbl for lbl, v in zip(["Income","Expense"], [inc, exp]) if v > 0]
        if sizes:
            plt.figure(); plt.title(f"Monthly Income vs Expense ({year}-{month:02d}) - Pie")
            plt.pie(sizes, labels=labels, autopct='%1.1f%%'); plt.tight_layout(); plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Could not plot monthly split: {e}")

def plot_yearly_split(year_var):
    try:
        year = int(year_var.get())
        d = model.yearly_income_expense(year)
        inc, exp = d.get("Income", 0.0), d.get("Expense", 0.0)
        if inc == 0 and exp == 0:
            messagebox.showinfo("No data", "No transactions for that year."); return

        plt.figure(); plt.title(f"Yearly Income vs Expense ({year}) - Bar")
        plt.bar(["Income","Expense"], [inc, exp]); plt.tight_layout(); plt.show()

        sizes = [v for v in [inc, exp] if v > 0]
        labels = [lbl for lbl, v in zip(["Income","Expense"], [inc, exp]) if v > 0]
        if sizes:
            plt.figure(); plt.title(f"Yearly Income vs Expense ({year}) - Pie")
            plt.pie(sizes, labels=labels, autopct='%1.1f%%'); plt.tight_layout(); plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Could not plot yearly split: {e}")

def on_export_csv():
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
    if not path: return
    rows = model.export_csv_rows()
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    messagebox.showinfo("Export", f"Exported {len(rows)-1} rows to {path}")

def on_import_csv(tree):
    path = filedialog.askopenfilename(filetypes=[("CSV","*.csv")])
    if not path: return
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    added = model.import_csv_rows(rows)
    refresh_table(tree)
    messagebox.showinfo("Import", f"Imported {added} rows.")

def build_gui(root):
    root.title("Python Financial Tracker")
    root.geometry("980x640")
    db.init_db()

    # Top frame: Add transaction
    top = ttk.LabelFrame(root, text="Add Transaction"); top.pack(fill="x", padx=10, pady=10)

    ttk.Label(top, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_date = ttk.Entry(top, width=15); entry_date.grid(row=0, column=1, padx=5, pady=5)
    entry_date.insert(0, date.today().strftime("%Y-%m-%d"))

    ttk.Label(top, text="Amount (+income, -expense):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    entry_amount = ttk.Entry(top, width=15); entry_amount.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(top, text="Category:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
    combo_cat = ttk.Combobox(top, values=CATEGORIES, width=18); combo_cat.grid(row=0, column=5, padx=5, pady=5); combo_cat.set("Other")

    ttk.Label(top, text="Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_desc = ttk.Entry(top, width=60); entry_desc.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky="we")

    btn_add = ttk.Button(top, text="Add", command=lambda: on_add(entry_date, entry_amount, combo_cat, entry_desc, tree))
    btn_add.grid(row=0, column=6, rowspan=2, padx=10, pady=5, sticky="ns")

    # Middle frame: Table
    mid = ttk.LabelFrame(root, text="Transactions"); mid.pack(fill="both", expand=True, padx=10, pady=10)
    cols = ("ID","Date","Amount","Category","Description")
    global tree
    tree = ttk.Treeview(mid, columns=cols, show="headings", height=15)
    for c in cols:
        tree.heading(c, text=c)
        width = 90 if c in ("ID","Date") else 120
        if c == "Description": width = 380
        tree.column(c, width=width, anchor="w")
    tree.pack(fill="both", expand=True, side="left")

    tree.bind("<Double-1>", lambda e: on_tree_double_click(e, tree))

    scrollbar = ttk.Scrollbar(mid, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")

    btns = ttk.Frame(root); btns.pack(fill="x", padx=10, pady=5)
    ttk.Button(btns, text="Edit Selected", command=lambda: on_edit(tree)).pack(side="left", padx=5)
    ttk.Button(btns, text="Delete Selected", command=lambda: on_delete(tree)).pack(side="left", padx=5)
    ttk.Button(btns, text="Export CSV", command=on_export_csv).pack(side="left", padx=5)
    ttk.Button(btns, text="Import CSV", command=lambda: on_import_csv(tree)).pack(side="left", padx=5)

    # Bottom frame: Charts
    bottom = ttk.LabelFrame(root, text="Charts"); bottom.pack(fill="x", padx=10, pady=10)
    ttk.Label(bottom, text="Year:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    year_var = tk.StringVar(value=str(date.today().year)); entry_year = ttk.Entry(bottom, textvariable=year_var, width=6); entry_year.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(bottom, text="Month (1-12):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    month_var = tk.StringVar(value=str(date.today().month)); entry_month = ttk.Entry(bottom, textvariable=month_var, width=4); entry_month.grid(row=0, column=3, padx=5, pady=5)

    ttk.Button(bottom, text="Plot Monthly (Categories)", command=lambda: plot_monthly(year_var, month_var)).grid(row=0, column=4, padx=10, pady=5)
    ttk.Button(bottom, text="Plot Yearly (Categories)", command=lambda: plot_yearly(year_var)).grid(row=0, column=5, padx=10, pady=5)
    ttk.Button(bottom, text="Monthly Income vs Expense", command=lambda: plot_monthly_split(year_var, month_var)).grid(row=1, column=4, padx=10, pady=5)
    ttk.Button(bottom, text="Yearly Income vs Expense", command=lambda: plot_yearly_split(year_var)).grid(row=1, column=5, padx=10, pady=5)

    # Menu
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Import CSV...", command=lambda: on_import_csv(tree))
    filemenu.add_command(label="Export CSV...", command=on_export_csv)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    refresh_table(tree)

def main():
    try:
        db.init_db()
        root = tk.Tk()
        build_gui(root)
        root.mainloop()
    except Exception as e:
        print("Fatal error: ", e)

if __name__ == "__main__":
    main()