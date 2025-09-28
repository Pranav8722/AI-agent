# create_sample_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Drop tables if they exist
cur.execute("DROP TABLE IF EXISTS employees;")
cur.execute("DROP TABLE IF EXISTS sales;")

# Create employees (messy column names)
cur.execute("""
CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY,
    full_name TEXT,
    dept_name TEXT,
    salary_usd INTEGER,
    joinDate TEXT,
    miscellaneous_col TEXT
);

""")

employees = [
    (1, "Alice Johnson", "Engineering", 125000, "2019-03-15", "x"),
    (2, "Bob Smith", "Sales", 98000, "2020-07-22", None),
    (3, "Charlie Lee", "Marketing", 115000, "2018-11-02", "n/a"),
    (4, "Diana Prince", "Engineering", 132000, "2021-01-12", "ok"),
    (5, "Evan Green", "Product", 107000, "2017-05-30", ""),
    (6, "Fay Zhao", "Engineering", 99000, "2022-08-08", None)
]
cur.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?);", employees)

# Create sales table (dirty data types)
cur.execute("""
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    product_name TEXT,
    region TEXT,
    revenue TEXT,
    sale_date TEXT
);
""")

sales = [
    (1, "Gadget Pro", "North", "10000", "2023-01-15"),
    (2, "Gadget Pro", "South", "8500", "2023-02-20"),
    (3, "Widget X", "East", "23000", "2022-11-05"),
    (4, "Widget X", "North", "null", "2023-03-08"),
    (5, "Service A", "West", "15000", "2023/04/10"),
    (6, "Gadget Pro", "North", "12000", "2023-05-01"),
    (7, "Service A", None, "7000", "2023-06-20")
]
cur.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?);", sales)

conn.commit()
conn.close()

print(f"Created DB at: {DB_PATH}")
