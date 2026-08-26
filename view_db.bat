@echo off
echo [*] Exporting live SQLite database decision_replay.db to human-readable format...
python export_db.py
echo.
echo [*] Displaying database snapshot in terminal...
python inspect_db.py
pause
