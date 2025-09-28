import os
import re
import sqlite3
from pathlib import Path
from groq import Groq
import pandas as pd
from backend.file_utils import execute_sql, generate_plot

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / (os.getenv("DB_FILE", "uploaded_data.db"))

# GROQ setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in environment")

client = Groq(api_key=GROQ_API_KEY)
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_schema_text():
    """Return the SQLite schema as text."""
    if not DB_PATH.exists():
        return "No tables loaded."
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    pieces = []
    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = [c[1] for c in cur.fetchall()]
        pieces.append(f"{t}({', '.join(cols)})")
    conn.close()
    return "\n".join(pieces) if pieces else "No tables loaded."


def clean_sql_output(text: str) -> str:
    """Extract SQL statement from LLM output."""
    m = re.search(r"```sql\n(.*?)```", text, re.S | re.I)
    if m:
        return m.group(1).strip()
    m = re.search(r"(SELECT .*?;)", text, re.S | re.I)
    if m:
        return m.group(1).strip()
    return text.strip()


def generate_sql(question: str) -> str:
    """Generate SQL query from natural language question."""
    schema = get_schema_text()
    prompt = f"""You are a SQL expert. Convert the question into a valid SQLite SQL query.
Use the schema below. If a column name has special characters, wrap in double quotes.
Return only the SQL (one statement, end with semicolon).

Schema:
{schema}

Question: {question}
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that outputs only SQL."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    raw = resp.choices[0].message.content
    sql = clean_sql_output(raw)
    return sql


def answer_question(question: str, agg_threshold: int = 50):
    """Answer question by generating SQL and returning results."""
    sql = generate_sql(question)
    if not sql or sql.lower().startswith("error"):
        return {"sql": sql, "answer": "Error generating SQL", "result": {"columns": [], "rows": []}, "plot": None}

    result = execute_sql(sql)
    plot = None
    aggregated_result = None

    if "error" not in result and result.get("rows"):
        try:
            df = pd.DataFrame(result["rows"], columns=result["columns"])
            num_cols = df.select_dtypes(include="number").columns.tolist()

            # Aggregate if rows exceed threshold
            if len(df) > agg_threshold and len(num_cols) >= 1:
                df = df.groupby(df.columns[0])[num_cols[0]].sum().reset_index()
                aggregated_result = df.to_dict(orient="records")

            # Generate plot using first column as X and first numeric as Y
            if len(df.columns) >= 2 and len(num_cols) >= 1:
                plot = generate_plot(df, df.columns[0], num_cols[0], kind="bar")

        except Exception:
            plot = None

    return {
        "sql": sql,
        "answer": "SQL executed successfully" if "error" not in result else f"Error: {result.get('error')}",
        "result": result,
        "aggregated_result": aggregated_result,
        "plot": plot
    }


def process_uploaded_file(file_path: str):
    """
    Reads the uploaded CSV or Excel file and returns its columns.
    """
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)  # requires openpyxl
        else:
            return {"error": "Unsupported file type."}

        columns = df.columns.tolist()
        return {"filename": os.path.basename(file_path), "columns": columns, "rows_count": len(df)}
    except Exception as e:
        return {"error": str(e)}
