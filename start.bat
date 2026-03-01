@echo off
echo Starting Attendance Analytics Dashboard...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI server...
echo.
echo Frontend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health:   http://localhost:8000/health
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
