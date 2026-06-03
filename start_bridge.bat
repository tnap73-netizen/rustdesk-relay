@echo off
for /f "delims=" %%i in ('dir /s /b C:\Users\tn_bridge_server.py 2^>nul') do set FOUND=%%i
if defined FOUND (
    set BRIDGE_SECRET=BGSM2024
    python "%FOUND%"
) else (
    echo File not found. Downloading now...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/tnap73-netizen/rustdesk-relay/main/tn_bridge_server.py' -OutFile 'C:\tn_bridge_server.py'"
    set BRIDGE_SECRET=BGSM2024
    python C:\tn_bridge_server.py
)
