import sqlite3
import os

DB_PATH = "decision_replay.db"

def inspect_database():
    if not os.path.exists(DB_PATH):
        print(f"[!] Database file '{DB_PATH}' does not exist. Run reset_db.bat to create it.")
        return

    print("=" * 60)
    print(f"  SQLITE DATABASE INSPECTOR: {DB_PATH}")
    print(f"  File size: {os.path.getsize(DB_PATH)} bytes")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"Found {len(tables)} tables: {', '.join(tables)}\n")

    for table in tables:
        print(f"--- [TABLE: {table.upper()}] ---")
        # Column names
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {', '.join(columns)}")

        # Row count & Sample Rows
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        print(f"Total Rows: {len(rows)}")
        for idx, row in enumerate(rows, 1):
            print(f"  Row {idx}: {row}")
        print()

    conn.close()
    print("=" * 60)
    print("  [OK] Database inspection completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    inspect_database()
