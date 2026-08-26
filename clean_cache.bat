@echo off
echo [*] Cleaning Python __pycache__ and cache artifacts...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo [OK] Python cache cleaned successfully!
