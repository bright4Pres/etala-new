@echo off
echo Starting Celery worker...
start powershell -NoExit -Command "cd '%~dp0'; & C:\Users\mycar\Downloads\Projects\Trooper\.venv\Scripts\Activate.ps1; celery -A lims_portal worker -l info -P gevent"

echo Starting Django development server...
start powershell -NoExit -Command "cd '%~dp0'; & C:\Users\mycar\Downloads\Projects\Trooper\.venv\Scripts\Activate.ps1; python manage.py runserver 8080"

echo Both services started!