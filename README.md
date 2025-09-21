# Python Financial Tracker

Financial Tracker is a simple Python app which allows users to input financial data, and get visual data representations through graphs and charts.

## Features

- Add / edit / delete transactions (date, amount, category, description)
- Import/Export CSV
- Charts with matplotlib:
- Category totals (bar) + expenses pie (per month/year)
- Income vs Expense split (bar + pie)
- Local storage in **SQLite** (`finance.db`, auto-created)

## Installation

**Windows:**

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

**Mac/Linux:**

```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```


## Usage

1. Enter **date** (YYYY-MM-DD), **amount** (+income, -expense), **category**, and **description**.
2. **Double click** a row (or **edit selected**) to modify.
3. **Import/Export** CSV for bulk data.
4. Use bottom controls to plot **monthly/yearly** charts.

## Sample Data

Import `sample_data.csv` to try charts right away.

## Project Structure

```bash
db.py        # SQLite init
model.py     # CRUD + reporting queries
main.py      # Tkinter GUI & charts
requirements.txt
sample_data.csv
```

## License

MIT