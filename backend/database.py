# database.py
import sqlite3
import os
from typing import Dict, Any

DB_FILE = os.path.join(os.path.dirname(__file__), "sample.db")

def execute_sql(query: str) -> Dict[str, Any]:
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        return {"columns": cols, "rows": rows}
    except Exception as e:
        return {"error": str(e)}

