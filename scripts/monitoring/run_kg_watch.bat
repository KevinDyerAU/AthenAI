@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Configure environment variables here or in System Environment Variables
REM Example defaults (edit as needed):
IF NOT DEFINED NEO4J_URI set NEO4J_URI=bolt://localhost:7687
IF NOT DEFINED NEO4J_USER set NEO4J_USER=neo4j
IF NOT DEFINED NEO4J_PASSWORD set NEO4J_PASSWORD=changeme
IF NOT DEFINED INTERVAL_SECONDS set INTERVAL_SECONDS=60
IF NOT DEFINED ALERT_MIN_SEVERITY set ALERT_MIN_SEVERITY=warning
IF NOT DEFINED THRESH_ORPHANS set THRESH_ORPHANS=0
IF NOT DEFINED THRESH_CONTRADICTIONS set THRESH_CONTRADICTIONS=0
IF NOT DEFINED THRESH_MISSING set THRESH_MISSING=0

REM Resolve repo root based on this script location
set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..\..
pushd %REPO_ROOT%

REM Call python watcher
python scripts\monitoring\kg_integrity_watch.py
set EXITCODE=%ERRORLEVEL%
popd
exit /b %EXITCODE%
