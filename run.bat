@echo off
echo ============================================
echo   JobGuard - Fake Job Posting Detector
echo ============================================

REM 1. Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

REM 2. Train model if not present
IF NOT EXIST "model\model.pkl" (
    echo Training ML model - first-time setup...
    python model\train_model.py
) ELSE (
    echo Model already trained. Skipping training.
)

REM 3. Start Flask server
echo.
echo Starting JobGuard at http://127.0.0.1:5000
echo Press Ctrl+C to stop.
echo.
python app.py
