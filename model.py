from typing import List, Tuple, Dict
from datetime import datetime
from db import get_conn

def add_transaction(t_date: str, amount: float, category: str, description: str = "") -> int:
    datetime.strptime(t_date, "%Y-%m-%d")
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO transactions (t_date, amount, category, description) VALUES (?,?,?,?)", (t_date, amount, category.strip(), description.strip()))
        conn.commit()
        return cur.lastrowid

def update_transaction(tid: int, t_date: str, amount: float, category: str, description: str = "") -> None:
    datetime.strptime(t_date, "%Y-%m-%d")
    with get_conn() as conn:
        conn.execute("UPDATE transactions SET t_date=?, amount=?, category=?, description=? WHERE id=?", (t_date, amount, category.strip(), description.strip(), tid))
        conn.commit()

def delete_transaction(tid: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM transactions WHERE id=?", (tid,))
        conn.commit()

def list_transactions(limit: int = 2000, offset: int = 0) -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, t_date, amount, category, description FROM transactions ORDER BY t_date DESC, id DESC LIMIT ? OFFSET ?", (limit, offset))
        return cur.fetchall()

def monthly_totals(year: int, month: int) -> Dict[str, float]:
    ym = f"{year:04d}-{month:02d}"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, SUM(amount) FROM transactions WHERE t_date LIKE ? GROUP BY category", (ym + "%",))
        return {cat: total for cat, total in cur.fetchall()}

def yearly_totals(year: int) -> Dict[str, float]:
    y = f"{year:04d}-"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, SUM(amount) FROM transactions WHERE t_date LIKE ? GROUP BY category", (y + "%",))
        return {cat: total for cat, total in cur.fetchall()}

def _income_expense_from_rows(rows: List[Tuple[str, float]]) -> Dict[str, float]:
    income = sum(v for _, v in rows if v > 0)
    expense = -sum(v for _, v in rows if v < 0)
    return {"Income": income, "Expense": expense}

def monthly_income_expense(year: int, month: int) -> Dict[str, float]:
    ym = f"{year:04d}-{month:02d}"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, amount FROM transactions WHERE t_date LIKE ?", (ym + "%",))
        rows = cur.fetchall()
    return _income_expense_from_rows(rows)

def yearly_income_expense(year: int) -> Dict[str, float]:
    y = f"{year:04d}-"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT category, amount FROM transactions WHERE t_date LIKE ?", (y + "%",))
        rows = cur.fetchall()
    return _income_expense_from_rows(rows)

def import_csv_rows(rows: List[List[str]]) -> int:
    count = 0
    with get_conn() as conn:
        cur = conn.cursor()
        for r in rows:
            if not r: continue
            if r[0].lower().startswith("t_date"):
                continue
            t_date, amount, category, description = (r + ["",""])[:4]
            try:
                datetime.strptime(t_date.strip(), "%Y-%m-%d")
                amt = float(amount)
            except Exception:
                continue
            cur.execute("INSERT INTO transactions (t_date, amount, category, description) VALUES (?,?,?,?)", (t_date.strip(), amt, category.strip(), (description or "").strip()))
            count += 1
        conn.commit()
    return count

def export_csv_rows() -> List[List[str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT t_date, amount, category, description FROM transactions ORDER BY t_date ASC, id ASC")
        rows = cur.fetchall()
    out = [["t_date","amount","category","description"]]
    out += [[r[0], str(r[1]), r[2], r[3] or ""] for r in rows]
    return out