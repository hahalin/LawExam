@echo off
cd /d D:\repo\LawExam
if not exist _rec mkdir _rec
echo START> _rec\status.txt
set PY=
where py >nul 2>&1 && set PY=py
if "%PY%"=="" (python -c "import sys" >nul 2>&1 && set PY=python)
if "%PY%"=="" (echo NO_PYTHON> _rec\status.txt & exit /b 1)
%PY% --version > _rec\log.txt 2>&1
echo INSTALLING> _rec\status.txt
%PY% -m pip install -q PyAudioWPatch >> _rec\log.txt 2>&1
%PY% scripts\record_loopback.py 110 _rec\clip.wav _rec\status.txt >> _rec\log.txt 2>&1
echo EXIT %ERRORLEVEL%>> _rec\status.txt
