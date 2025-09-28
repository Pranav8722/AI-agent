# backend/file_utils.py
import os
import sqlite3
import pandas as pd
from pathlib import Path
from fastapi import UploadFile
import matplotlib.pyplot as plt
import io
import base64

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
DB_PATH = BASE_DIR / (os.getenv("DB_FILE", "uploaded_data.db"))

def save_file(upload_file: UploadFile) -> Path:
    dest = UPLOAD_DIR / upload_file.filename
    with open(dest, "wb") as f:
        f.write(upload_file.file.read())
    return dest

def load_excel(file_path: Path, table_name="data"):
    df = pd.read_excel(file_path)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return list(df.columns)

def load_csv(file_path: Path, table_name="data"):
    df = pd.read_csv(file_path)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return list(df.columns)

def load_pdf(file_path: Path, table_name="data"):
    # Requires tabula-py and Java OR camelot+ghostscript
    try:
        import tabula
    except Exception as e:
        raise RuntimeError("tabula-py not installed or Java missing for PDF parsing.") from e

    dfs = tabula.read_pdf(str(file_path), pages="all", multiple_tables=True)
    if not dfs:
        return []
    df = pd.concat(dfs, ignore_index=True)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    return list(df.columns)

def execute_sql(sql: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        if cur.description:
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            conn.close()
            return {"columns": cols, "rows": rows}
        else:
            conn.commit()
            conn.close()
            return {"columns": [], "rows": []}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

def generate_plot(df: pd.DataFrame, x_column, y_column, kind="bar"):
    plt.figure(figsize=(6,4))
    if kind == "bar":
        df.plot(kind="bar", x=x_column, y=y_column)
    elif kind == "line":
        df.plot(kind="line", x=x_column, y=y_column)
    else:
        df.plot(x=x_column, y=y_column)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
