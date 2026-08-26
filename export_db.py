import sqlite3
import json
import os

DB_PATH = "decision_replay.db"
OUTPUT_MD = "docs/database_data_view.md"
OUTPUT_JSON = "docs/database_export.json"

def export_database():
    if not os.path.exists(DB_PATH):
        print(f"[!] Database '{DB_PATH}' not found. Run reset_db.bat first.")
        return

    os.makedirs("docs", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]

    db_export = {}
    md_lines = [
        "# 🗄️ SQLite Database Snapshot (`decision_replay.db`)",
        f"**File Size:** {os.path.getsize(DB_PATH)} bytes | **Tables:** {len(tables)}\n",
        "> This document is automatically generated to view SQLite database tables directly in your text editor.\n"
    ]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        records = [dict(zip(cols, row)) for row in rows]
        db_export[table] = {
            "columns": cols,
            "total_rows": len(rows),
            "rows": records
        }

        md_lines.append(f"## Table: `{table.upper()}` ({len(rows)} records)")
        if len(rows) == 0:
            md_lines.append("_No records in this table currently._\n")
        else:
            header = "| " + " | ".join(cols) + " |"
            divider = "| " + " | ".join(["---"] * len(cols)) + " |"
            md_lines.append(header)
            md_lines.append(divider)
            for row in rows:
                row_str = "| " + " | ".join([str(v) if v is not None else "`NULL`" for v in row]) + " |"
                md_lines.append(row_str)
            md_lines.append("\n")

    conn.close()

    # Write Markdown view
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    # Write JSON view
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(db_export, f, indent=2, default=str)

    print(f"[OK] Database exported successfully!")
    print(f" -> Readable Markdown: {OUTPUT_MD}")
    print(f" -> Readable JSON: {OUTPUT_JSON}")

if __name__ == "__main__":
    export_database()
